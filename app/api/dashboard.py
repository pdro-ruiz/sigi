
"""
API Router para dashboard y reportes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.models.database import get_db
from app.models.schemas import DashboardStats
from app.services.database_service import DatabaseService
from app.services.analytics_service import AnalyticsService

router = APIRouter()
analytics_service = AnalyticsService()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas generales del dashboard"""
    try:
        stats = DatabaseService.get_dashboard_stats(db)
        
        # Agregar estadísticas adicionales
        additional_stats = await analytics_service.get_additional_stats(db)
        stats.update(additional_stats)
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

@router.get("/metrics/resolution-time")
async def get_resolution_time_metrics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtener métricas de tiempo de resolución"""
    try:
        metrics = await analytics_service.get_resolution_time_metrics(db, days)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo métricas de resolución: {str(e)}")

@router.get("/metrics/category-trends")
async def get_category_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtener tendencias por categoría"""
    try:
        trends = await analytics_service.get_category_trends(db, days)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo tendencias: {str(e)}")

@router.get("/metrics/sentiment-analysis")
async def get_sentiment_metrics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtener análisis de sentimientos agregado"""
    try:
        sentiment_data = await analytics_service.get_sentiment_metrics(db, days)
        return sentiment_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo análisis de sentimientos: {str(e)}")

@router.get("/metrics/priority-distribution")
async def get_priority_distribution(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtener distribución por prioridad"""
    try:
        distribution = await analytics_service.get_priority_distribution(db, days)
        return distribution
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo distribución de prioridades: {str(e)}")

@router.get("/metrics/daily-incidents")
async def get_daily_incidents(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtener incidencias por día"""
    try:
        daily_data = await analytics_service.get_daily_incidents(db, days)
        return daily_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos diarios: {str(e)}")

@router.get("/reports/summary")
async def get_summary_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Generar reporte resumen"""
    try:
        report = await analytics_service.generate_summary_report(
            db, start_date, end_date, category
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")

@router.get("/reports/performance")
async def get_performance_report(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Generar reporte de rendimiento"""
    try:
        report = await analytics_service.generate_performance_report(db, days)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte de rendimiento: {str(e)}")

@router.get("/live-stats")
async def get_live_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas en tiempo real"""
    try:
        live_stats = await analytics_service.get_live_stats(db)
        return live_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas en vivo: {str(e)}")
