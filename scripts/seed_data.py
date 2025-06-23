
"""
Script para cargar datos de ejemplo en la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.models.database import SessionLocal, create_tables, Incident, User, Response, MLPrediction
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Crear datos de ejemplo para testing"""
    db = SessionLocal()
    
    try:
        # Crear usuarios de ejemplo
        users = [
            User(username="admin", email="admin@sigi.local", role="admin"),
            User(username="tecnico1", email="tecnico1@sigi.local", role="technician"),
            User(username="tecnico2", email="tecnico2@sigi.local", role="technician"),
            User(username="usuario1", email="usuario1@sigi.local", role="user"),
            User(username="usuario2", email="usuario2@sigi.local", role="user"),
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        
        # Crear incidencias de ejemplo
        sample_incidents = [
            {
                "title": "Error de autenticación en login",
                "description": "Los usuarios no pueden acceder al sistema, aparece error de credenciales inválidas",
                "category": "authentication",
                "priority": "high",
                "status": "open"
            },
            {
                "title": "Lentitud en carga de reportes",
                "description": "Los reportes tardan más de 30 segundos en cargar, impactando productividad",
                "category": "performance", 
                "priority": "medium",
                "status": "in_progress"
            },
            {
                "title": "Falla integración con API externa",
                "description": "La sincronización con el sistema externo no funciona desde ayer",
                "category": "integration",
                "priority": "critical",
                "status": "open"
            },
            {
                "title": "Datos duplicados en base de datos",
                "description": "Se están creando registros duplicados al guardar información",
                "category": "data",
                "priority": "high",
                "status": "open"
            },
            {
                "title": "Botón de guardar no responde",
                "description": "En la pantalla de configuración, el botón guardar no hace nada al hacer click",
                "category": "ui_bug",
                "priority": "medium",
                "status": "resolved"
            },
            {
                "title": "Error 500 en dashboard principal",
                "description": "Al acceder al dashboard aparece error interno del servidor",
                "category": "performance",
                "priority": "critical",
                "status": "open"
            },
            {
                "title": "Problema con permisos de usuario",
                "description": "Algunos usuarios ven opciones que no deberían según su rol",
                "category": "authentication",
                "priority": "medium",
                "status": "in_progress"
            },
            {
                "title": "Backup automático falló",
                "description": "El backup programado no se ejecutó anoche, revisar configuración",
                "category": "data",
                "priority": "high",
                "status": "open"
            }
        ]
        
        incidents = []
        for i, incident_data in enumerate(sample_incidents):
            incident = Incident(
                **incident_data,
                sentiment_score=random.uniform(-1, 1),
                urgency_level=random.choice(["low", "medium", "high", "critical"]),
                created_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                assigned_to=random.choice(["tecnico1", "tecnico2", None])
            )
            
            if incident.status == "resolved":
                incident.resolved_at = incident.created_at + timedelta(hours=random.randint(1, 48))
                incident.resolution_notes = "Problema resuelto correctamente"
            
            incidents.append(incident)
            db.add(incident)
        
        db.commit()
        
        # Crear respuestas de ejemplo
        sample_responses = [
            Response(
                incident_id=1,
                user_id=2,
                message="Estoy revisando el problema de autenticación. Parece ser un issue con la configuración del servidor.",
                is_automated=False
            ),
            Response(
                incident_id=1,
                user_id=1,
                message="Basado en el análisis automático, este problema está relacionado con la configuración de SSL. Revisa los certificados.",
                is_automated=True
            ),
            Response(
                incident_id=2,
                user_id=3,
                message="He identificado que la lentitud se debe a consultas no optimizadas en la base de datos.",
                is_automated=False
            ),
        ]
        
        for response in sample_responses:
            db.add(response)
        
        db.commit()
        
        # Crear predicciones ML de ejemplo
        for incident in incidents:
            # Predicción de categoría
            category_prediction = MLPrediction(
                incident_id=incident.id,
                model_name="DistilBERT-classification",
                prediction_type="category",
                prediction_value=incident.category,
                confidence_score=random.uniform(0.7, 0.95)
            )
            db.add(category_prediction)
            
            # Predicción de sentimiento
            sentiment_prediction = MLPrediction(
                incident_id=incident.id,
                model_name="BERT-sentiment",
                prediction_type="sentiment",
                prediction_value=random.choice(["positive", "neutral", "negative"]),
                confidence_score=random.uniform(0.6, 0.9)
            )
            db.add(sentiment_prediction)
        
        db.commit()
        
        print("✅ Datos de ejemplo creados correctamente")
        print(f"   - {len(users)} usuarios")
        print(f"   - {len(incidents)} incidencias")
        print(f"   - {len(sample_responses)} respuestas")
        print(f"   - {len(incidents) * 2} predicciones ML")
        
    except Exception as e:
        print(f"❌ Error creando datos de ejemplo: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Creando datos de ejemplo...")
    create_tables()
    create_sample_data()
