from fastapi import FastAPI
from app.database.connection import engine, Base
from app.models.user import User
from app.api.user_api import router as user_router

app = FastAPI(
    title="AI Cybersecurity Platform",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(user_router)

@app.get("/")
def root():
    return {
        "message": "AI Cybersecurity Platform Running"
    }