
"""
Servicio de Machine Learning para SIGI Local
Incluye clasificación, análisis de sentimientos, detección de duplicados y generación de respuestas
"""

import re
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import numpy as np
from datetime import datetime

# Para evitar errores si los modelos no están disponibles, usaremos implementaciones simples
class MockTransformer:
    """Mock transformer para cuando los modelos reales no estén disponibles"""
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    def predict(self, text: str) -> Dict[str, Any]:
        # Implementación simple basada en palabras clave
        return self._keyword_based_prediction(text)
    
    def _keyword_based_prediction(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        # Clasificación basada en palabras clave
        if any(word in text_lower for word in ['login', 'password', 'access', 'permission', 'authentication', 'auth']):
            category = "authentication"
        elif any(word in text_lower for word in ['slow', 'performance', 'speed', 'timeout', 'lag', 'lento']):
            category = "performance"
        elif any(word in text_lower for word in ['api', 'integration', 'sync', 'connection', 'integración']):
            category = "integration"
        elif any(word in text_lower for word in ['data', 'database', 'duplicate', 'backup', 'datos']):
            category = "data"
        else:
            category = "ui_bug"
        
        # Análisis de urgencia
        if any(word in text_lower for word in ['critical', 'urgent', 'emergency', 'down', 'crítico', 'urgente']):
            urgency = "critical"
        elif any(word in text_lower for word in ['important', 'high', 'priority', 'importante', 'alto']):
            urgency = "high"
        elif any(word in text_lower for word in ['minor', 'low', 'pequeño', 'bajo']):
            urgency = "low"
        else:
            urgency = "medium"
        
        # Análisis de sentimiento simple
        negative_words = ['error', 'problem', 'issue', 'fail', 'broken', 'problema', 'falla', 'error']
        positive_words = ['good', 'working', 'fine', 'solved', 'bueno', 'funciona', 'resuelto']
        
        neg_count = sum(1 for word in negative_words if word in text_lower)
        pos_count = sum(1 for word in positive_words if word in text_lower)
        
        if neg_count > pos_count:
            sentiment = "negative"
            score = -0.7
        elif pos_count > neg_count:
            sentiment = "positive"
            score = 0.7
        else:
            sentiment = "neutral"
            score = 0.0
        
        return {
            'category': category,
            'urgency': urgency,
            'sentiment': sentiment,
            'sentiment_score': score
        }

from app.models.schemas import (
    ClassificationResult, SentimentResult, UrgencyResult, 
    DuplicateCandidate, SuggestedResponse, AnalysisResult,
    CategoryEnum, UrgencyEnum, PredictionCreate
)
from app.services.database_service import DatabaseService

class MLService:
    """Servicio principal de Machine Learning"""
    
    def __init__(self):
        self.classifier = MockTransformer("classification")
        self.sentiment_analyzer = MockTransformer("sentiment")
        self.duplicate_detector = MockTransformer("duplicates")
        self.response_templates = self._load_response_templates()
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Cargar plantillas de respuestas predefinidas"""
        return {
            "authentication": [
                "Por favor verifica tus credenciales e intenta nuevamente. Si el problema persiste, contacta al administrador del sistema.",
                "Este parece ser un problema de autenticación. Revisa que tu usuario y contraseña sean correctos.",
                "Para problemas de acceso, asegúrate de que tu cuenta esté activa y los permisos sean correctos."
            ],
            "performance": [
                "Estamos investigando los problemas de rendimiento. Te mantendremos informado sobre el progreso.",
                "Para mejorar el rendimiento, intenta cerrar otras aplicaciones y verificar tu conexión a internet.",
                "Hemos identificado el problema de lentitud y estamos trabajando en optimizar el sistema."
            ],
            "integration": [
                "El problema de integración está siendo revisado por nuestro equipo técnico. Tendremos una actualización pronto.",
                "Para problemas de sincronización, verifica que todos los servicios externos estén funcionando correctamente.",
                "Estamos trabajando en restablecer la conexión con el sistema externo."
            ],
            "data": [
                "Los problemas de datos están siendo investigados. Realizaremos una verificación de integridad de la base de datos.",
                "Para problemas de duplicados, ejecutaremos un proceso de limpieza de datos en las próximas horas.",
                "Estamos realizando una verificación completa de la consistencia de los datos."
            ],
            "ui_bug": [
                "Hemos registrado el problema de interfaz y lo incluiremos en la próxima actualización.",
                "Para problemas de interfaz, intenta refrescar la página o limpiar el caché del navegador.",
                "El error de interfaz ha sido documentado y será corregido en una próxima versión."
            ]
        }
    
    async def classify_incident(self, title: str, description: str) -> ClassificationResult:
        """Clasificar incidencia en una de las 5 categorías"""
        try:
            text = f"{title} {description}"
            result = self.classifier.predict(text)
            
            return ClassificationResult(
                category=CategoryEnum(result['category']),
                confidence=0.85  # Confidence simulada
            )
        except Exception as e:
            # Fallback a categoría por defecto
            return ClassificationResult(
                category=CategoryEnum.ui_bug,
                confidence=0.5
            )
    
    async def analyze_sentiment(self, title: str, description: str) -> SentimentResult:
        """Analizar sentimiento del texto"""
        try:
            text = f"{title} {description}"
            result = self.sentiment_analyzer.predict(text)
            
            return SentimentResult(
                sentiment=result['sentiment'],
                score=result['sentiment_score']
            )
        except Exception as e:
            return SentimentResult(
                sentiment="neutral",
                score=0.0
            )
    
    async def analyze_urgency(self, title: str, description: str) -> UrgencyResult:
        """Analizar nivel de urgencia"""
        try:
            text = f"{title} {description}"
            result = self.classifier.predict(text)
            
            return UrgencyResult(
                urgency=UrgencyEnum(result['urgency']),
                confidence=0.8
            )
        except Exception as e:
            return UrgencyResult(
                urgency=UrgencyEnum.medium,
                confidence=0.5
            )
    
    async def find_duplicates(self, title: str, description: str, db: Session) -> List[DuplicateCandidate]:
        """Encontrar posibles incidencias duplicadas"""
        try:
            # Obtener todas las incidencias para comparar
            incidents = DatabaseService.get_incidents(db, limit=1000)
            duplicates = []
            
            for incident in incidents:
                # Cálculo simple de similitud basado en palabras comunes
                similarity = self._calculate_text_similarity(
                    f"{title} {description}",
                    f"{incident.title} {incident.description}"
                )
                
                if similarity > 0.6:  # Umbral de similitud
                    duplicates.append(DuplicateCandidate(
                        incident_id=incident.id,
                        title=incident.title,
                        similarity_score=similarity
                    ))
            
            # Ordenar por similitud descendente
            duplicates.sort(key=lambda x: x.similarity_score, reverse=True)
            return duplicates[:5]  # Devolver top 5
            
        except Exception as e:
            return []
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calcular similitud entre dos textos usando Jaccard similarity"""
        def tokenize(text):
            return set(re.findall(r'\w+', text.lower()))
        
        tokens1 = tokenize(text1)
        tokens2 = tokenize(text2)
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    async def suggest_response(self, title: str, description: str, category: Optional[str] = None) -> List[SuggestedResponse]:
        """Sugerir respuestas automáticas"""
        try:
            # Si no se proporciona categoría, clasificar primero
            if not category:
                classification = await self.classify_incident(title, description)
                category = classification.category.value
            
            # Obtener plantillas para la categoría
            templates = self.response_templates.get(category, self.response_templates["ui_bug"])
            
            suggestions = []
            for i, template in enumerate(templates):
                suggestions.append(SuggestedResponse(
                    template_id=i + 1,
                    content=template,
                    relevance_score=0.9 - (i * 0.1)  # Decrementa relevancia
                ))
            
            return suggestions
            
        except Exception as e:
            # Respuesta genérica en caso de error
            return [SuggestedResponse(
                template_id=1,
                content="Gracias por reportar esta incidencia. Nuestro equipo está revisando el problema y te contactaremos pronto con una solución.",
                relevance_score=0.7
            )]
    
    async def analyze_incident(self, incident_id: int, title: str, description: str, db: Session) -> AnalysisResult:
        """Realizar análisis completo de una incidencia"""
        try:
            # Ejecutar todos los análisis en paralelo
            classification_task = self.classify_incident(title, description)
            sentiment_task = self.analyze_sentiment(title, description)
            urgency_task = self.analyze_urgency(title, description)
            duplicates_task = self.find_duplicates(title, description, db)
            
            # Esperar resultados
            classification = await classification_task
            sentiment = await sentiment_task
            urgency = await urgency_task
            duplicates = await duplicates_task
            
            # Generar respuestas sugeridas basadas en la clasificación
            suggested_responses = await self.suggest_response(
                title, description, classification.category.value
            )
            
            # Guardar predicciones en base de datos
            await self._save_predictions(incident_id, classification, sentiment, urgency, db)
            
            return AnalysisResult(
                incident_id=incident_id,
                classification=classification,
                sentiment=sentiment,
                urgency=urgency,
                duplicates=duplicates,
                suggested_responses=suggested_responses
            )
            
        except Exception as e:
            # En caso de error, devolver análisis básico
            return AnalysisResult(
                incident_id=incident_id,
                classification=ClassificationResult(category=CategoryEnum.ui_bug, confidence=0.5),
                sentiment=SentimentResult(sentiment="neutral", score=0.0),
                urgency=UrgencyResult(urgency=UrgencyEnum.medium, confidence=0.5),
                duplicates=[],
                suggested_responses=[]
            )
    
    async def _save_predictions(self, incident_id: int, classification: ClassificationResult, 
                              sentiment: SentimentResult, urgency: UrgencyResult, db: Session):
        """Guardar predicciones en base de datos"""
        try:
            # Predicción de categoría
            category_prediction = PredictionCreate(
                incident_id=incident_id,
                model_name="MockClassifier",
                prediction_type="category",
                prediction_value=classification.category.value,
                confidence_score=classification.confidence
            )
            DatabaseService.create_prediction(db, category_prediction)
            
            # Predicción de sentimiento
            sentiment_prediction = PredictionCreate(
                incident_id=incident_id,
                model_name="MockSentiment",
                prediction_type="sentiment",
                prediction_value=sentiment.sentiment,
                confidence_score=abs(sentiment.score)
            )
            DatabaseService.create_prediction(db, sentiment_prediction)
            
            # Predicción de urgencia
            urgency_prediction = PredictionCreate(
                incident_id=incident_id,
                model_name="MockUrgency",
                prediction_type="urgency",
                prediction_value=urgency.urgency.value,
                confidence_score=urgency.confidence
            )
            DatabaseService.create_prediction(db, urgency_prediction)
            
        except Exception as e:
            print(f"Error guardando predicciones: {e}")
    
    async def process_feedback(self, feedback_data):
        """Procesar feedback para mejorar modelos"""
        # En una implementación real, aquí se reentrenarían los modelos
        # Por ahora solo registramos el feedback
        print(f"Feedback recibido: {feedback_data}")
        return True
    
    async def get_model_performance_stats(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de rendimiento de modelos"""
        try:
            # Contar predicciones por modelo
            predictions = db.query(
                DatabaseService.MLPrediction.model_name,
                DatabaseService.MLPrediction.prediction_type,
                db.func.count(DatabaseService.MLPrediction.id).label('count'),
                db.func.avg(DatabaseService.MLPrediction.confidence_score).label('avg_confidence')
            ).group_by(
                DatabaseService.MLPrediction.model_name,
                DatabaseService.MLPrediction.prediction_type
            ).all()
            
            stats = {
                "total_predictions": sum(p.count for p in predictions),
                "models": {}
            }
            
            for prediction in predictions:
                model_name = prediction.model_name
                if model_name not in stats["models"]:
                    stats["models"][model_name] = {}
                
                stats["models"][model_name][prediction.prediction_type] = {
                    "count": prediction.count,
                    "average_confidence": round(prediction.avg_confidence or 0, 3)
                }
            
            return stats
            
        except Exception as e:
            return {
                "total_predictions": 0,
                "models": {},
                "error": str(e)
            }
