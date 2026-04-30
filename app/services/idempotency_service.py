from app.models.processed_message import ProcessedMessage

def is_duplicate(db, message_id: str) -> bool:
    return db.query(ProcessedMessage).filter_by(message_id=message_id).first() is not None

def save_message(db, message_id: str):
    record = ProcessedMessage(message_id=message_id)
    db.add(record)
    db.commit()
