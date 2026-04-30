import os
import httpx
from fastapi import Depends, APIRouter, Request
from dotenv import load_dotenv

from app.utils import extract_message
from app.intent import detect_intent
from app.executor import handle_intent

from app.memory import get_user_context, update_user_context, clear_user_context

from app.ledger import get_or_create_user, get_or_create_default_group

from app.db import get_db

from sqlalchemy.orm import Session

load_dotenv()

router = APIRouter()

processed_messages = set()

def is_duplicate(message_id: str) -> bool:
    if message_id in processed_messages:
        return True

    processed_messages.add(message_id)
    return False


async def send_whatsapp_message(to: str, message: str):
    url = f"https://graph.facebook.com/v22.0/{os.getenv('WHATSAPP_PHONE_ID')}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        return await client.post(url, json=payload, headers=headers)


@router.get("/webhook")
async def verify(request: Request):
    params = request.query_params

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == os.getenv("VERIFY_TOKEN")
    ):
        return int(params.get("hub.challenge"))

    return {"status": "error"}


@router.post("/webhook")
async def receive_message(request: Request, db: Session = Depends(get_db)):

    payload = await request.json()

    # 1. Extract message safely
    result = extract_message(payload)
    if not result:
        return {"status": "ignored"}

    message, sender, message_id = result
    text = message.get("text", {}).get("body", "").strip().lower()

    print(f"{sender}: {text}")

    try:
        # 2. Get or create user
        user = get_or_create_user(db, sender)

        # 3. Ensure group exists
        group = get_or_create_default_group(db)

        if not user.group_id:
            user.group_id = group.id

        # 4. Load memory
        context = get_user_context(sender)

        # 5. ONBOARDING FLOW
        if not user.opt_in and not context:
            response = (
                "Welcome to Warima\n\n"
                "We help you save and manage your Stokvel.\n\n"
                "Do you agree to receive messages?\n"
                "1 Yes\n2 No"
            )
            update_user_context(sender, {"onboarding": "awaiting_opt_in"})
            await send_whatsapp_message(sender, response)
            db.commit()
            return {"status": "onboarding"}

        # 6. Handle opt-in
        if context.get("onboarding") == "awaiting_opt_in":

            if text in ["1", "yes"]:
                user.opt_in = True
                response = "Great! What's your name?"
                update_user_context(sender, {"onboarding": "awaiting_name"})

            elif text in ["2", "no"]:
                response = "No problem. Message me anytime."
                clear_user_context(sender)

            else:
                response = "Please reply:\n1 Yes\n2 No"

            await send_whatsapp_message(sender, response)
            db.commit()
            return {"status": "onboarding"}

        # 7. Handle name capture
        if context.get("onboarding") == "awaiting_name":
            user.name = text.title()

            response = f"Nice to meet you, {user.name}. You're all set!"

            clear_user_context(sender)

            await send_whatsapp_message(sender, response)
            db.commit()
            return {"status": "onboarding_done"}

        # 8. Intent pipeline
        intent_data = detect_intent(text, context)

        response, new_context = handle_intent(
            intent_data,
            context,
            sender,
            db,
            user
        )

        # 9. Memory update
        if new_context:
            update_user_context(sender, new_context)
        else:
            clear_user_context(sender)

        # 10. Reply
        await send_whatsapp_message(sender, response)

        db.commit()

        return {"status": "ok"}

    except Exception as e:
        db.rollback()
        raise e
