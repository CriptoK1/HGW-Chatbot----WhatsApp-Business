# backend/app/models/chatbot.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Conversation(Base):
    """Modelo para las conversaciones del chatbot"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    user_name = Column(String(100))
    status = Column(String(50), default="nuevo")
    profile_type = Column(String(50), default="otro")
    last_interaction = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "user_name": self.user_name,
            "status": self.status,
            "profile_type": self.profile_type,
            "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Message(Base):
    """Modelo para los mensajes del chatbot"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' o 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    conversation = relationship("Conversation", back_populates="messages")
    
    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

class Lead(Base):
    """Modelo para los leads (prospectos)"""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    user_name = Column(String(100))
    email = Column(String(100))
    profile_type = Column(String(50))
    interest_level = Column(Integer, default=5)  # 0-10
    status = Column(String(50), default="nuevo")  # nuevo, contactado, calificado, convertido, descartado
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "user_name": self.user_name,
            "email": self.email,
            "profile_type": self.profile_type,
            "interest_level": self.interest_level,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
