from app.services.messaging_service import send_message
from app.services.idempotency_service import is_duplicate, save_message
from app.services.state_machine import handle_state, is_active_flow
from app.intent import detect_intent
from app.executor import handle_intent

from app.models.session import UserSession

def extract_message(payload: dict):
    try:
        entry = payload.get("entry", [])
        if not entry:
            return None

        changes = entry[0].get("changes", [])
        if not changes:
            return None

        value = changes[0].get("value", {})

        messages = value.get("messages", [])
        if not messages:
            return None

        msg = messages[0]

        message_id = msg.get("id")
        user_id = msg.get("from")

        text = msg.get("text", {}).get("body")

        if not message_id or not user_id:
            return None

        return {
            "id": message_id,
            "from": user_id,
            "text": (text or "").strip().lower()
        }

    except Exception as e:
        print("extract_message error:", e)
        return None

async def handle_incoming_message(payload, db):
    message = extract_message(payload)

    if not message:
        return

    message_id = message["id"]
    user_id = message["from"]
    text = message["text"]

    if is_duplicate(db, message_id):
        return

    save_message(db, message_id)

    session = db.query(UserSession).filter_by(user_id=user_id).first()

    context = session.context if session and session.context else {}

    if is_active_flow(session):
        response = await handle_state(db, user_id. text)
        await send_message(user_id, response)
        return

    intent_data = detect_intent(text, context)

    response, new_context, next_action = handle_intent(
        intent_data,
        context,
        user_id,
        db
    )

    await send_message(user_id, response)
