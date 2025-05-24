from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, Message

router = APIRouter()

class MessageSchema(BaseModel):
    user: str
    content: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/messages")
async def add_message(message: MessageSchema, db: Session = Depends(get_db)):
    db_message = Message(user=message.user, content=message.content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return {"status": "message added", "id": db_message.id}

@router.get("/messages")
async def get_messages(db: Session = Depends(get_db)):
    messages = db.query(Message).all()
    return messages
