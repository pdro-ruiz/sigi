
"""
API Router para análisis con IA
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.database import get_db
from app.models.schemas import *
from app.services.database_service import DatabaseService
from app.services.ml_service import MLService

router = APIRouter()
ml_service = MLService()

class AnalyzeRequest(BaseModel):
    title: str
    description: str

class FeedbackRequest(BaseModel):
    incident_id: int
    prediction_id: int
    user_id: int
    feedback_type: str  # "correct" or "incorrect"
    correct_value: Optional[str] = None

@router.post("/classify", response_model=ClassificationResult)
async def classify_text(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """Clasificar texto en categorías"""
    try:
        result = await ml_service.classify_incident(
            request.title, request.description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en clasificación: {str(e)}")

@router.post("/sentiment", response_model=SentimentResult)
async def analyze_sentiment(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """Analizar sentimiento del texto"""
    try:
        result = await ml_service.analyze_sentiment(
            request.title, request.description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis de sentimiento: {str(e)}")

@router.post("/urgency", response_model=UrgencyResult)
async def analyze_urgency(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """Analizar nivel de urgencia"""
    try:
        result = await ml_service.analyze_urgency(
            request.title, request.description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis de urgencia: {str(e)}")

@router.post("/duplicates")
async def find_duplicates(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """Encontrar incidencias duplicadas"""
    try:
        duplicates = await ml_service.find_duplicates(
            request.title, request.description, db
        )
        return {"duplicates": duplicates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detectando duplicados: {str(e)}")

@router.post("/suggest-response")
async def suggest_response(
    request: AnalyzeRequest,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Sugerir respuesta automática"""
    try:
        suggestions = await ml_service.suggest_response(
            request.title, request.description, category
        )
        return {"suggested_responses": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando respuesta: {str(e)}")

@router.post("/complete/{incident_id}", response_model=AnalysisResult)
async def complete_analysis(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Realizar análisis completo de una incidencia"""
    # Verificar que la incidencia existe
    incident = DatabaseService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    
    try:
        analysis_result = await ml_service.analyze_incident(
            incident_id, incident.title, incident.description, db
        )
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis completo: {str(e)}")

@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """Enviar feedback para mejorar modelos ML"""
    try:
        feedback_data = FeedbackCreate(**feedback.dict())
        db_feedback = DatabaseService.create_feedback(db, feedback_data)
        
        # Actualizar métricas del modelo (implementar según necesidades)
        await ml_service.process_feedback(feedback_data)
        
        return {
            "message": "Feedback recibido correctamente",
            "feedback_id": db_feedback.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando feedback: {str(e)}")

@router.get("/predictions/{incident_id}")
async def get_predictions(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Obtener predicciones ML de una incidencia"""
    try:
        predictions = DatabaseService.get_incident_predictions(db, incident_id)
        return {"predictions": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo predicciones: {str(e)}")

@router.get("/model-stats")
async def get_model_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas de rendimiento de modelos ML"""
    try:
        stats = await ml_service.get_model_performance_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")
