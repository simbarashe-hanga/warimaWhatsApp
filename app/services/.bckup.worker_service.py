from app.services.queue_service import (
    get_and_mark_processing,
    mark_done,
    mark_failed
)

from app.models.user_session import UserSession
from app.engine.intent import detect_intent
from app.engine.executor import handle_intent
from app.services.messaging_service import send_message


async def process_event(db):
    event = get_and_mark_processing(db)

    if not event:
        return False

    try:
        mark_processing(db, event)

        user_id = event.user_id
        text = event.payload["text"]

        session = db.query(UserSession).filter_by(user_id=user_id).first()

        context = session.context if session and session.context else {}

        intent_data = detect_intent(text, context)

        response, new_context, _ = handle_intent(
            intent_data,
            context,
            user_id,
            db
        )

        # update session
        if session:
            session.cotext = new_context or {}
            db.commit()

        await send_message(user_id, response)

        mark_done(db, event)

    except Exception as e:
        print("Worker error:", e)
        mark_failed(db, event)

    return True
