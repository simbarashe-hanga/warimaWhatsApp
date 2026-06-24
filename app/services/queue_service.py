from app.models.event_queue import EventQueue
from sqlalchemy.orm import Session


def enqueue_event(db: Session, message: dict):
    event = EventQueue(
        message_id=message["id"],
        user_id=message["user_id"],
        payload=message,
        status="PENDING",
        attempts=0
    )
    db.add(event)
    db.commit()


def get_and_mark_processing(db: Session):
    event = (
        db.query(EventQueue)
        .filter_by(status="PENDING")
        .order_by(EventQueue.created_at)
        .with_for_update(skip_locked=True)
        .first()
    )

    if not event:
        return None

    event.status = "PROCESSING"
    event.attempts += 1

    db.commit()
    db.refresh(event)

    return event



def mark_done(db: Session, event: EventQueue):
    event.status = "DONE"
    db.commit()

MAX_RETRIES = 3


def mark_failed(db, event, error):
    if event.attempts < MAX_RETRIES:
        event.status = "PENDING"
    else:
        event.status = "FAILED"

    event.error = str(error)[:255]

    db.commit()
