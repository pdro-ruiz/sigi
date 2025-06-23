
"""
Servicios para operaciones de base de datos
"""

from sqlalchemy.orm import Session
from app.models.database import Incident, User, Response, MLPrediction, Feedback
from app.models.schemas import IncidentCreate, IncidentUpdate, UserCreate, ResponseCreate, PredictionCreate, FeedbackCreate
from typing import List, Optional
from datetime import datetime
import sqlalchemy as sa

class DatabaseService:
    
    @staticmethod
    def create_incident(db: Session, incident: IncidentCreate) -> Incident:
        """Crear nueva incidencia"""
        db_incident = Incident(**incident.dict())
        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)
        return db_incident
    
    @staticmethod
    def get_incident(db: Session, incident_id: int) -> Optional[Incident]:
        """Obtener incidencia por ID"""
        return db.query(Incident).filter(Incident.id == incident_id).first()
    
    @staticmethod
    def get_incidents(db: Session, skip: int = 0, limit: int = 100, 
                     category: Optional[str] = None, 
                     status: Optional[str] = None,
                     priority: Optional[str] = None) -> List[Incident]:
        """Obtener lista de incidencias con filtros"""
        query = db.query(Incident)
        
        if category:
            query = query.filter(Incident.category == category)
        if status:
            query = query.filter(Incident.status == status)
        if priority:
            query = query.filter(Incident.priority == priority)
            
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_incident(db: Session, incident_id: int, incident_update: IncidentUpdate) -> Optional[Incident]:
        """Actualizar incidencia"""
        db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if db_incident:
            update_data = incident_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_incident, field, value)
            db_incident.updated_at = datetime.now()
            db.commit()
            db.refresh(db_incident)
        return db_incident
    
    @staticmethod
    def delete_incident(db: Session, incident_id: int) -> bool:
        """Eliminar incidencia"""
        db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if db_incident:
            db.delete(db_incident)
            db.commit()
            return True
        return False
    
    @staticmethod
    def search_incidents(db: Session, query: str) -> List[Incident]:
        """Buscar incidencias por texto"""
        search_filter = f"%{query}%"
        return db.query(Incident).filter(
            sa.or_(
                Incident.title.ilike(search_filter),
                Incident.description.ilike(search_filter)
            )
        ).all()
    
    @staticmethod
    def get_dashboard_stats(db: Session) -> dict:
        """Obtener estadísticas para dashboard"""
        total_incidents = db.query(Incident).count()
        open_incidents = db.query(Incident).filter(Incident.status == "open").count()
        resolved_incidents = db.query(Incident).filter(Incident.status == "resolved").count()
        
        # Distribución por categoría
        category_stats = db.query(
            Incident.category, 
            sa.func.count(Incident.id)
        ).group_by(Incident.category).all()
        
        # Distribución por prioridad
        priority_stats = db.query(
            Incident.priority,
            sa.func.count(Incident.id)
        ).group_by(Incident.priority).all()
        
        return {
            "total_incidents": total_incidents,
            "open_incidents": open_incidents,
            "resolved_incidents": resolved_incidents,
            "incidents_by_category": dict(category_stats),
            "incidents_by_priority": dict(priority_stats)
        }
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Crear nuevo usuario"""
        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_response(db: Session, response: ResponseCreate) -> Response:
        """Crear nueva respuesta"""
        db_response = Response(**response.dict())
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        return db_response
    
    @staticmethod
    def get_incident_responses(db: Session, incident_id: int) -> List[Response]:
        """Obtener respuestas de una incidencia"""
        return db.query(Response).filter(Response.incident_id == incident_id).all()
    
    @staticmethod
    def create_prediction(db: Session, prediction: PredictionCreate) -> MLPrediction:
        """Crear nueva predicción ML"""
        db_prediction = MLPrediction(**prediction.dict())
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        return db_prediction
    
    @staticmethod
    def get_incident_predictions(db: Session, incident_id: int) -> List[MLPrediction]:
        """Obtener predicciones de una incidencia"""
        return db.query(MLPrediction).filter(MLPrediction.incident_id == incident_id).all()
    
    @staticmethod
    def create_feedback(db: Session, feedback: FeedbackCreate) -> Feedback:
        """Crear feedback para mejorar modelo"""
        db_feedback = Feedback(**feedback.dict())
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        return db_feedback
