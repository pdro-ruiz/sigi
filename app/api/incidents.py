
"""
API Router para gestión de incidencias
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.database import get_db
from app.models.schemas import *
from app.services.database_service import DatabaseService
from app.services.ml_service import MLService

router = APIRouter()
ml_service = MLService()

@router.post("/", response_model=Incident)
async def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db)
):
    """Crear nueva incidencia con análisis automático de IA"""
    try:
        # Crear incidencia en base de datos
        db_incident = DatabaseService.create_incident(db, incident)
        
        # Realizar análisis automático con IA
        analysis_result = await ml_service.analyze_incident(
            db_incident.id,
            db_incident.title,
            db_incident.description,
            db
        )
        
        # Actualizar incidencia con resultados del análisis
        update_data = IncidentUpdate(
            category=analysis_result.classification.category,
            urgency_level=analysis_result.urgency.urgency
        )
        
        updated_incident = DatabaseService.update_incident(
            db, db_incident.id, update_data
        )
        
        return updated_incident
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando incidencia: {str(e)}")

@router.get("/", response_model=List[Incident])
async def get_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener lista de incidencias con filtros"""
    try:
        incidents = DatabaseService.get_incidents(
            db, skip=skip, limit=limit,
            category=category, status=status, priority=priority
        )
        return incidents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo incidencias: {str(e)}")

@router.get("/{incident_id}", response_model=Incident)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Obtener incidencia específica por ID"""
    incident = DatabaseService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    return incident

@router.put("/{incident_id}", response_model=Incident)
async def update_incident(
    incident_id: int,
    incident_update: IncidentUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar incidencia existente"""
    try:
        updated_incident = DatabaseService.update_incident(
            db, incident_id, incident_update
        )
        if not updated_incident:
            raise HTTPException(status_code=404, detail="Incidencia no encontrada")
        return updated_incident
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando incidencia: {str(e)}")

@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar incidencia"""
    try:
        success = DatabaseService.delete_incident(db, incident_id)
        if not success:
            raise HTTPException(status_code=404, detail="Incidencia no encontrada")
        return {"message": "Incidencia eliminada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando incidencia: {str(e)}")

@router.get("/search/{query}", response_model=List[Incident])
async def search_incidents(
    query: str,
    db: Session = Depends(get_db)
):
    """Buscar incidencias por texto"""
    try:
        incidents = DatabaseService.search_incidents(db, query)
        return incidents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")

@router.get("/{incident_id}/responses", response_model=List[Response])
async def get_incident_responses(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Obtener respuestas de una incidencia"""
    # Verificar que la incidencia existe
    incident = DatabaseService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    
    try:
        responses = DatabaseService.get_incident_responses(db, incident_id)
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo respuestas: {str(e)}")

@router.post("/{incident_id}/responses", response_model=Response)
async def create_incident_response(
    incident_id: int,
    response: ResponseCreate,
    db: Session = Depends(get_db)
):
    """Crear respuesta para una incidencia"""
    # Verificar que la incidencia existe
    incident = DatabaseService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    
    try:
        # Asegurar que el incident_id coincida
        response.incident_id = incident_id
        db_response = DatabaseService.create_response(db, response)
        return db_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando respuesta: {str(e)}")
