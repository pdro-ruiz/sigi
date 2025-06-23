
"""
Servicio de Analytics para métricas y reportes del dashboard
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

from app.models.database import Incident, Response, MLPrediction, User

class AnalyticsService:
    """Servicio para análisis y métricas del sistema"""
    
    async def get_additional_stats(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas adicionales para el dashboard"""
        try:
            # Tiempo promedio de resolución
            resolved_incidents = db.query(Incident).filter(
                Incident.status == "resolved",
                Incident.resolved_at.isnot(None)
            ).all()
            
            resolution_times = []
            for incident in resolved_incidents:
                if incident.resolved_at and incident.created_at:
                    delta = incident.resolved_at - incident.created_at
                    resolution_times.append(delta.total_seconds() / 3600)  # En horas
            
            avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
            
            # Distribución de sentimientos
            sentiment_predictions = db.query(
                MLPrediction.prediction_value,
                func.count(MLPrediction.id)
            ).filter(
                MLPrediction.prediction_type == "sentiment"
            ).group_by(MLPrediction.prediction_value).all()
            
            sentiment_distribution = dict(sentiment_predictions)
            
            return {
                "average_resolution_time": round(avg_resolution_time, 2),
                "sentiment_distribution": sentiment_distribution
            }
            
        except Exception as e:
            return {
                "average_resolution_time": 0,
                "sentiment_distribution": {}
            }
    
    async def get_resolution_time_metrics(self, db: Session, days: int) -> Dict[str, Any]:
        """Obtener métricas de tiempo de resolución"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Incidencias resueltas en el período
            resolved_incidents = db.query(Incident).filter(
                and_(
                    Incident.status == "resolved",
                    Incident.created_at >= cutoff_date,
                    Incident.resolved_at.isnot(None)
                )
            ).all()
            
            # Calcular métricas por categoría
            metrics_by_category = {}
            all_times = []
            
            for incident in resolved_incidents:
                if incident.resolved_at and incident.created_at:
                    resolution_time = (incident.resolved_at - incident.created_at).total_seconds() / 3600
                    all_times.append(resolution_time)
                    
                    category = incident.category or "unknown"
                    if category not in metrics_by_category:
                        metrics_by_category[category] = []
                    metrics_by_category[category].append(resolution_time)
            
            # Calcular estadísticas
            result = {
                "period_days": days,
                "total_resolved": len(resolved_incidents),
                "overall_avg": round(sum(all_times) / len(all_times), 2) if all_times else 0,
                "by_category": {}
            }
            
            for category, times in metrics_by_category.items():
                result["by_category"][category] = {
                    "avg_hours": round(sum(times) / len(times), 2),
                    "min_hours": round(min(times), 2),
                    "max_hours": round(max(times), 2),
                    "count": len(times)
                }
            
            return result
            
        except Exception as e:
            return {
                "period_days": days,
                "total_resolved": 0,
                "overall_avg": 0,
                "by_category": {},
                "error": str(e)
            }
    
    async def get_category_trends(self, db: Session, days: int) -> Dict[str, Any]:
        """Obtener tendencias por categoría"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Incidencias por categoría en el período
            category_trends = db.query(
                Incident.category,
                func.date(Incident.created_at).label('date'),
                func.count(Incident.id).label('count')
            ).filter(
                Incident.created_at >= cutoff_date
            ).group_by(
                Incident.category,
                func.date(Incident.created_at)
            ).order_by(desc('date')).all()
            
            # Organizar datos para gráficos
            trends_data = {}
            for trend in category_trends:
                category = trend.category or "unknown"
                date_str = str(trend.date)
                
                if category not in trends_data:
                    trends_data[category] = {}
                
                trends_data[category][date_str] = trend.count
            
            return {
                "period_days": days,
                "trends": trends_data
            }
            
        except Exception as e:
            return {
                "period_days": days,
                "trends": {},
                "error": str(e)
            }
    
    async def get_sentiment_metrics(self, db: Session, days: int) -> Dict[str, Any]:
        """Obtener métricas de análisis de sentimientos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Predicciones de sentimiento en el período
            sentiment_data = db.query(
                MLPrediction.prediction_value,
                MLPrediction.confidence_score,
                func.date(MLPrediction.created_at).label('date')
            ).join(Incident).filter(
                and_(
                    MLPrediction.prediction_type == "sentiment",
                    Incident.created_at >= cutoff_date
                )
            ).all()
            
            # Agregar por sentimiento y fecha
            daily_sentiment = {}
            sentiment_summary = {"positive": 0, "neutral": 0, "negative": 0}
            
            for data in sentiment_data:
                date_str = str(data.date)
                sentiment = data.prediction_value
                
                if date_str not in daily_sentiment:
                    daily_sentiment[date_str] = {"positive": 0, "neutral": 0, "negative": 0}
                
                daily_sentiment[date_str][sentiment] += 1
                sentiment_summary[sentiment] += 1
            
            return {
                "period_days": days,
                "daily_sentiment": daily_sentiment,
                "summary": sentiment_summary,
                "total_analyzed": sum(sentiment_summary.values())
            }
            
        except Exception as e:
            return {
                "period_days": days,
                "daily_sentiment": {},
                "summary": {"positive": 0, "neutral": 0, "negative": 0},
                "total_analyzed": 0,
                "error": str(e)
            }
    
    async def get_priority_distribution(self, db: Session, days: int) -> Dict[str, Any]:
        """Obtener distribución por prioridad"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            priority_data = db.query(
                Incident.priority,
                Incident.status,
                func.count(Incident.id).label('count')
            ).filter(
                Incident.created_at >= cutoff_date
            ).group_by(
                Incident.priority,
                Incident.status
            ).all()
            
            # Organizar datos
            distribution = {}
            for data in priority_data:
                priority = data.priority or "unknown"
                status = data.status
                
                if priority not in distribution:
                    distribution[priority] = {}
                
                distribution[priority][status] = data.count
            
            return {
                "period_days": days,
                "distribution": distribution
            }
            
        except Exception as e:
            return {
                "period_days": days,
                "distribution": {},
                "error": str(e)
            }
    
    async def get_daily_incidents(self, db: Session, days: int) -> Dict[str, Any]:
        """Obtener incidencias por día"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            daily_data = db.query(
                func.date(Incident.created_at).label('date'),
                func.count(Incident.id).label('created'),
                func.sum(func.case([(Incident.status == 'resolved', 1)], else_=0)).label('resolved')
            ).filter(
                Incident.created_at >= cutoff_date
            ).group_by(
                func.date(Incident.created_at)
            ).order_by('date').all()
            
            # Formatear datos para gráficos
            chart_data = []
            for data in daily_data:
                chart_data.append({
                    "date": str(data.date),
                    "created": data.created,
                    "resolved": data.resolved or 0
                })
            
            return {
                "period_days": days,
                "daily_data": chart_data
            }
            
        except Exception as e:
            return {
                "period_days": days,
                "daily_data": [],
                "error": str(e)
            }
    
    async def generate_summary_report(self, db: Session, start_date: Optional[str], 
                                    end_date: Optional[str], category: Optional[str]) -> Dict[str, Any]:
        """Generar reporte resumen"""
        try:
            # Construir query base
            query = db.query(Incident)
            
            # Aplicar filtros de fecha
            if start_date:
                query = query.filter(Incident.created_at >= datetime.fromisoformat(start_date))
            if end_date:
                query = query.filter(Incident.created_at <= datetime.fromisoformat(end_date))
            if category:
                query = query.filter(Incident.category == category)
            
            incidents = query.all()
            
            # Calcular métricas
            total = len(incidents)
            resolved = len([i for i in incidents if i.status == "resolved"])
            open_incidents = len([i for i in incidents if i.status == "open"])
            in_progress = len([i for i in incidents if i.status == "in_progress"])
            
            # Distribuciones
            category_dist = {}
            priority_dist = {}
            
            for incident in incidents:
                cat = incident.category or "unknown"
                pri = incident.priority or "unknown"
                
                category_dist[cat] = category_dist.get(cat, 0) + 1
                priority_dist[pri] = priority_dist.get(pri, 0) + 1
            
            return {
                "period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "category_filter": category
                },
                "summary": {
                    "total_incidents": total,
                    "resolved": resolved,
                    "open": open_incidents,
                    "in_progress": in_progress,
                    "resolution_rate": round((resolved / total * 100), 2) if total > 0 else 0
                },
                "distributions": {
                    "by_category": category_dist,
                    "by_priority": priority_dist
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "summary": {},
                "distributions": {}
            }
    
    async def generate_performance_report(self, db: Session, days: int) -> Dict[str, Any]:
        """Generar reporte de rendimiento"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Métricas de rendimiento
            total_incidents = db.query(Incident).filter(Incident.created_at >= cutoff_date).count()
            resolved_incidents = db.query(Incident).filter(
                and_(
                    Incident.created_at >= cutoff_date,
                    Incident.status == "resolved"
                )
            ).count()
            
            # Tiempo promedio de primera respuesta
            first_responses = db.query(
                func.min(Response.created_at).label('first_response'),
                Incident.created_at
            ).join(Incident).filter(
                Incident.created_at >= cutoff_date
            ).group_by(Incident.id).all()
            
            response_times = []
            for resp in first_responses:
                if resp.first_response and resp.created_at:
                    delta = resp.first_response - resp.created_at
                    response_times.append(delta.total_seconds() / 3600)
            
            avg_first_response = sum(response_times) / len(response_times) if response_times else 0
            
            return {
                "period_days": days,
                "performance_metrics": {
                    "total_incidents": total_incidents,
                    "resolved_incidents": resolved_incidents,
                    "resolution_rate": round((resolved_incidents / total_incidents * 100), 2) if total_incidents > 0 else 0,
                    "avg_first_response_hours": round(avg_first_response, 2),
                    "incidents_per_day": round(total_incidents / days, 2)
                }
            }
            
        except Exception as e:
            return {
                "period_days": days,
                "performance_metrics": {},
                "error": str(e)
            }
    
    async def get_live_stats(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas en tiempo real"""
        try:
            now = datetime.now()
            today = now.date()
            
            # Estadísticas del día actual
            today_incidents = db.query(Incident).filter(
                func.date(Incident.created_at) == today
            ).count()
            
            today_resolved = db.query(Incident).filter(
                and_(
                    func.date(Incident.created_at) == today,
                    Incident.status == "resolved"
                )
            ).count()
            
            # Incidencias activas
            active_incidents = db.query(Incident).filter(
                Incident.status.in_(["open", "in_progress"])
            ).count()
            
            # Últimas 24 horas
            last_24h = now - timedelta(hours=24)
            incidents_24h = db.query(Incident).filter(
                Incident.created_at >= last_24h
            ).count()
            
            return {
                "timestamp": now.isoformat(),
                "today": {
                    "incidents_created": today_incidents,
                    "incidents_resolved": today_resolved
                },
                "active_incidents": active_incidents,
                "last_24h_incidents": incidents_24h
            }
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
