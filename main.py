from dotenv import load_dotenv
load_dotenv()

import sys
import os
import shutil
from pathlib import Path

# Use __file__ to get the current script's directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_core import AIPersonality
from database import get_db, engine
from models import Base, User, Message

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


# Ensure database tables are created
Base.metadata.create_all(bind=engine)

# Create uploads directory
UPLOAD_DIR = Path("uploads") 
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize FastAPI app
app = FastAPI(title="Zena - Multilingual AI Chatbot", version="2.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Personality
ai_personality = AIPersonality(use_gemini=True)


# Pydantic Models
class UserCreate(BaseModel):
    name: str
    personality: str


# Routes
@app.get("/")
async def root():
    """Root endpoint - API status check"""
    return {
        "message": "Zena AI Backend is running!", 
        "version": "2.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment platforms"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "Zena AI Chatbot"
    }


@app.get("/chat")
async def serve_frontend():
    """Serve the frontend HTML interface"""
    return FileResponse("multilingual_chat_frontend.html")


@app.post("/users/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user with custom personality"""
    db_user = User(name=user.name, personality=user.personality)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "id": db_user.id, 
        "name": db_user.name, 
        "personality": db_user.personality
    }


@app.post("/chat/")
async def chat(
    message: str = Form(...),
    personality: str = Form(...),
    user_id: int = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Handle chat messages with optional image/video uploads"""
    image_path = None
    image_url = None

    # Handle file upload
    if file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix
        filename = f"{user_id}_{timestamp}{file_extension}"
        file_path = UPLOAD_DIR / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image_path = str(file_path)
        image_url = f"/uploads/{filename}"

    # Save user message to database
    user_message = Message(
        user_id=user_id,
        sender="user",
        content=message,
        image_url=image_url,
        timestamp=datetime.utcnow()
    )
    db.add(user_message)
    db.commit()

    # Generate AI reply
    try:
        ai_reply = ai_personality.generate_ai_reply(
            user_input=message,
            personality=personality,
            image_path=image_path
        )
    except Exception as e:
        print(f"Error generating AI reply: {e}")
        ai_reply = "Sorry, I'm having trouble responding right now. Please try again."

    # Save AI message to database
    ai_message = Message(
        user_id=user_id,
        sender="ai",
        content=ai_reply,
        timestamp=datetime.utcnow()
    )
    db.add(ai_message)
    db.commit()

    return {"reply": ai_reply}


@app.get("/chat/history/{user_id}")
async def get_chat_history(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve chat history for a specific user"""
    user_exists = db.query(User).filter(User.id == user_id).first()
    if not user_exists:
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


# Mount static files directory for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not found", "status_code": 404}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "status_code": 500}