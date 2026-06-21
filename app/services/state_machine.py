from app.services.messaging_service import send_message
from app.intent import detect_intent
from app.executor import handle_intent
from app.models.session import UserSession
from app.services.transaction_service import create_or_get_transaction


def is_active_flow(session) -> bool:
    return session and session.context and session.context.get("step") is not None

async def handle_state(db, user_id: str, text: str):
    session = db.query(UserSession).filter_by(user_id=user_id).first()

    if not session:
        session = UserSession(user_id=user_id, state="IDLE", context={})
        db.add(session)
        db.commit()

    if session.state != "IDLE":
        return await handle_fsm(db, session, user_id, text)

    intent_data = detect_intent(text, session.context or {})

    response, new_context, _ = handle_intent(
        intent_data,
        session.context,
        user_id,
        db
    )

    if new_context:
        session.context = new_context
        session.state = "IN_FLOW"
    else:
        session.context = {}
        session.state = "IDLE"

    db.commit()

    await send_message(user_id, response)

async def handle_fsm(db, session, user_id, text):
    context = session.context or {}

    if context.get("step") == "awaiting_amount":
        if text.isdigit():
            amount = int(text)

            session.context = {
                "flow": "contribution",
                "step": "awaiting_confirmation",
                "amount": amount
            }
            db.commit()

            await send_message(
                user_id,
                f"Confirm R{amount}? Reply 1 to confirm, 2 to cancel."
            )

    elif context.get("step") == "awaiting_confirmation":
        if text == "1":
            amount = context.get("amount")
            txn = create_or_get_transaction(db, user_id, amount)

            session.state = "IDLE"
            session.context = {}
            db.commit()

            await send_message(
                user_id,
                f"Contribution of R{amount} received. ID: {txn.id}"
            )

        elif text == "2":
            session.state = "IDLE"
            session.context = {}
            db.commit()

            await send_message(user_id, "Cancelled.")
