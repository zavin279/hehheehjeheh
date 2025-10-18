import sys
import os
import shutil
from pathlib import Path

# CRITICAL FIX 1: Use __file__ to get the current script's directory
# This helps Python find local modules like ai_core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# FIX: Changed import from ai_logic to ai_core to avoid module shadowing
from ai_core import AIPersonality
from database import get_db, engine
from models import Base, User, Message

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


# Ensure database tables are created
Base.metadata.create_all(bind=engine)

# CRITICAL FIX 2: Replaced smart quotes with straight quotes for the path
UPLOAD_DIR = Path("uploads") 
UPLOAD_DIR.mkdir(exist_ok=True)

# CRITICAL FIX 3: Replaced smart quotes in the FastAPI title/version
app = FastAPI(title="Multilingual AI Chatbot with Vision", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    # CRITICAL FIX 4: Replaced smart quotes in CORSMiddleware arguments
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_personality = AIPersonality(use_gemini=True)

class UserCreate(BaseModel):
    name: str
    personality: str

# CRITICAL FIX 5: Replaced smart quotes in the route decorator
@app.post("/users/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, personality=user.personality)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # CRITICAL FIX 6: Replaced smart quotes in the return dictionary
    return {"id": db_user.id, "name": db_user.name, "personality": db_user.personality}

# CRITICAL FIX 7: Replaced smart quotes in the route decorator
@app.post("/chat/")
async def chat(
    message: str = Form(...),
    personality: str = Form(...),
    user_id: int = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    image_path = None
    image_url = None

    if file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix
        filename = f"{user_id}_{timestamp}{file_extension}"
        file_path = UPLOAD_DIR / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image_path = str(file_path)
        image_url = f"/uploads/{filename}"

    user_message = Message(
        user_id=user_id,
        sender="user",
        content=message,
        image_url=image_url,
        timestamp=datetime.utcnow()
    )
    db.add(user_message)
    db.commit()

    ai_reply = ai_personality.generate_ai_reply(
        user_input=message,
        personality=personality,
        image_path=image_path
    )

    ai_message = Message(
        user_id=user_id,
        sender="ai",
        content=ai_reply,
        timestamp=datetime.utcnow()
    )
    db.add(ai_message)
    db.commit()

    return {"reply": ai_reply}


# CRITICAL FIX 8: Replaced smart quotes in the route decorator
@app.get("/chat/history/{user_id}")
async def get_chat_history(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(User.id == user_id).first()
    if not user_exists:
        # CRITICAL FIX 9: Replaced smart quotes in HTTPException detail
        raise HTTPException(status_code=404, detail="User not found.")

    messages = (
        db.query(Message)
        .filter(Message.user_id == user_id)
        .order_by(Message.timestamp.asc())
        .limit(limit)
        .all()
    )

    return {
        "messages": [
            {
                "id": msg.id,
                "sender": msg.sender,
                "content": msg.content,
                "image_url": msg.image_url,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    }


@app.get("/")
async def root():
    return {"message": "Zena AI Backend is running!", "version": "2.0.0"}

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# Add this at the bottom
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Serve the frontend
from fastapi.responses import FileResponse

@app.get("/chat")
async def serve_frontend():
    return FileResponse("multilingual_chat_frontend.html")