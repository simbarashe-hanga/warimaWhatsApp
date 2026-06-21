from app.db.session import engine
from app.models.conversation import ConversationMessage
from app.db.base import Base


Base.metadata.create_all(bind=engine)

print("done")
