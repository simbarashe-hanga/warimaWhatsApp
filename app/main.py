from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from app.api.routes import webhook
from app.db.init_db import init_db

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(webhook.router, prefix="/webhook")
