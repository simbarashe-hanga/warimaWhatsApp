from app.models.transaction import Transaction
import uuid

def create_or_get_transaction(db, user_id: str, amount: int):
    key = f"{user_id}:{amount}"

    txn = db.query(Transaction).filter_by(idempotency_key=key).first()

    if txn:
        return txn

    txn = Transaction(
        id=str(uuid.uuid4()),
        user_id=user_id,
        amount=amount,
        status="pending",
        idempotency_key=key
    )

    db.add(txn)
    db.commit()

    return txn
