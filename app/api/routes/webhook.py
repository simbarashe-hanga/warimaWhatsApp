from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.whatsapp_service import handle_incoming_message


router = APIRouter()

@router.post("")
async def receive_webhook(payload: dict, db: Session = Depends(get_db)):
    await handle_incoming_message(payload, db)
    return {"status": "ok"}
