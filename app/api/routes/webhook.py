from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.idempotency_service import is_duplicate, save_message
from app.services.queue_service import enqueue_event
from app.utils.extract_message import extract_message

router = APIRouter()


@router.post("")
async def receive_webhook(payload: dict, db: Session = Depends(get_db)):
    message = extract_message(payload)

    print("EXTRACTED:", message)

    if not message:
        print("NO MESSAGE")
        return {"status": "ignored"}

    print("CHECKING DUPLICATE")

    duplicate = is_duplicate(db, message["id"])
    print("DUPLICATE?", duplicate)

    if duplicate:
        return {"status": "duplicate"}

    print("SAVING MESSAGE")
    save_message(db, message["id"])

    print("ENQUEUEING")
    enqueue_event(db, message)

    print("DONE")

    return {"status": "queued"}


@router.get("/health")
def health(db: Session = Depends(get_db)):
    return {"status": "ok"}
