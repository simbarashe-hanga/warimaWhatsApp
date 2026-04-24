import os
import httpx
from fastapi import Depends, APIRouter, Request
from dotenv import load_dotenv

from app.utils import extract_message
from app.intent import detect_intent
from app.executor import handle_intent

from app.memory import get_user_context, update_user_context, clear_user_context

from app.ledger import get_or_create_user

from app.db import get_db

from sqlalchemy.orm import Session

load_dotenv()

router = APIRouter()

def save_user(db: Session, user):
    db.add(user)
    db.commit()
    db.refresh(user)

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
        response = await client.post(url, json=payload, headers=headers)

    print("WA STATUS:", response.status_code)
    print("WA RESPONSE:", response.text)

    return response


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

    sender = (
        payload.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("messages", [{}])[0]
        .get("from")
    )

    if not sender:
        return {"status": "no sender"}

    user = get_or_create_user(db, sender)
    save_user(db, user)

    result = extract_message(payload)
    if not result:
        return {"status": "ignored"}

    message, sender_id = result
    text = message.get("text", {}).get("body", "").strip().lower()

    print(f"{sender_id}: {text}")

    # 0. Ensure user exists
    user = get_or_create_user(db, sender_id)

    # 1. Load memory
    context = get_user_context(sender_id)

    # 2. Onboarding Flow
    if not user.opt_in and not context:
        response = (
            "Welcome to Warima\n\n"
            "We help you save in groups.\n\n"
            "Do you agree to receive messages?\n"
            "1 Yes\n2 No"
        )
        update_user_context(sender, {"onboarding": "awaiting_opt_in"})
        await send_whatsapp_message(sender, response)
        return {"status": "onboarding"}

    # Handle response to opt-in
    if context.get("onboarding") == "awaiting_opt_in":
        if text in ["1", "yes"]:
            user.opt_in = True
            # make sure to commit to DB
            save_user(db, user)

            response = "Great! What's your name?"
            update_user_context(sender, {"onboarding": "awaiting_name"})

        elif text in ["2", "no"]:
            response = "No problem. Message me anytime to start."
            clear_user_context(sender)

        else:
            response = "Please reply with:\n1 Yes\n2 No"

        await send_whatsapp_message(sender, response)
        return {"status": "onboarding"}

    if context.get("onboarding") == "awaiting_name":
        user.name = text.title()
        save_user(db, user)

        response = f"Nice to meet you, {user.name} \n\n You're all set!"

        clear_user_context(sender)

        await send_whatsapp_message(sender, response)
        return {"status": "onboarding_done"}


    # 2. Intent
    intent_data = detect_intent(text, context)

    # 3. Execute
    response, new_context = handle_intent(intent_data, context, sender, db)

    # 4. Save memory
    if new_context:
        update_user_context(sender, new_context)
    else:
        clear_user_context(sender)

    # 5. Reply
    await send_whatsapp_message(sender, response)

    return {"status": "ok"}
