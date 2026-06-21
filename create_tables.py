from app.db.session import Base, engine

from app.models.session import UserSession
from app.models.transaction import Transaction
from app.models.processed_message import ProcessedMessage
from app.models.event_queue import EventQueue
from app.models.conversation import ConversationMessage


Base.metadata.create_all(bind=engine)

print("Tables created.")
