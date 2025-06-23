
"""
Modelos de base de datos para SIGI Local
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100))
    priority = Column(String(50))
    status = Column(String(50), default="open")
    sentiment_score = Column(Float)
    urgency_level = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    assigned_to = Column(String(100))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    duplicate_of = Column(Integer, ForeignKey("incidents.id"))
    
    # Relaciones
    responses = relationship("Response", back_populates="incident")
    predictions = relationship("MLPrediction", back_populates="incident")
    duplicates = relationship("Incident", remote_side=[id])

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), default="user")
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)
    
    # Relaciones
    responses = relationship("Response", back_populates="user")

class Response(Base):
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_automated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relaciones
    incident = relationship("Incident", back_populates="responses")
    user = relationship("User", back_populates="responses")

class MLPrediction(Base):
    __tablename__ = "ml_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    prediction_type = Column(String(100), nullable=False)
    prediction_value = Column(Text, nullable=False)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=func.now())
    
    # Relaciones
    incident = relationship("Incident", back_populates="predictions")

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    prediction_id = Column(Integer, ForeignKey("ml_predictions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    feedback_type = Column(String(50), nullable=False)  # correct/incorrect
    correct_value = Column(Text)  # valor correcto si feedback es incorrect
    created_at = Column(DateTime, default=func.now())

# Configuración de la base de datos
from config.settings import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crear todas las tablas"""
    Base.metadata.create_all(bind=engine)
