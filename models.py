from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # Store the user-defined personality string here
    personality = Column(Text) 

    messages = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sender = Column(String)  # "user" or "ai"
    content = Column(Text)
    image_url = Column(String, nullable=True)  # NEW: Store image/video URL
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")