from app.db.base import Base
from app.db.session import engine

# import All models so that register
from app.models import processed_message, session, transaction

def init_db():
    Base.metadata.create_all(bind=engine)
