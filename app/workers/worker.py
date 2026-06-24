from dotenv import load_dotenv
from app.services.llm_service import chat

import asyncio
from app.db.session import SessionLocal

from app.services.queue_service import (
    get_and_mark_processing,
    mark_done,
    mark_failed
)

from app.services.conversation_service import (
    save_message,
    get_recent_messages
)

from app.services.messaging_service import send_message
from app.engine.intent import detect_intent
from app.engine.executor import handle_intent
from app.models.session import UserSession

load_dotenv()

async def process_message(db, event):
    message = event.payload

    user_id = message["user_id"]
    text = message.get("text", "").lower()

    print("EVENT:", message)
    print("USER:", user_id)
    print("TEXT:", text)

    # Load session or create session
    session = db.query(UserSession).filter_by(user_id=user_id).first()

    if not session:
        session = UserSession(user_id=user_id, context={})
        db.add(session)
        db.commit()

    context = session.context or {}

    context_text = f"""
    Current user state:

    {context}
    """

    save_message(
        db,
        user_id,
        "user",
        text
    )

    # Intent detection
    intent_data = detect_intent(text, context)
    print("INTENT:", intent_data)

    if intent_data["intent"] == "unknown":

        print("ROUTING TO LLM")

        history = get_recent_messages(
            db,
            user_id,
            limit=10
        )

        try:
            response = await chat(
                user_message=text,
                history=history
            )

        except Exception as e:
            print("LLM ERROR:", e)

            response = (
                "Warima AI is temporarily unavailable."
                "Please try again shortly."
            )

        print("LLM RESPONSE:", response)

        new_context = context

    else:

        response, new_context, _ = handle_intent(
            intent_data,
            context,
            user_id,
            db
        )

    save_message(
        db,
        user_id,
        "assistant",
        response
    )


    print("RESPONSE:", response)

    # Update context
    session.context = new_context or {}
    db.commit()

    # Send reply
    await send_message(user_id, response)


async def worker_loop():
    print("Worker started...")

    while True:
        try:
            db = SessionLocal()

            event = get_and_mark_processing(db)

            if event:
                try:
                    await process_message(db, event)
                    mark_done(db, event)

                except Exception as e:
                    print("Worker error:", e)
                    mark_failed(db, event, str(e))

            db.close()

        except Exception as e:
            print("Database unavailable:", e)

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(worker_loop())
