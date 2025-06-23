
"""
Configuración global del sistema SIGI Local
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base de datos
    database_url: str = "sqlite:///data/database/sigi_local.db"
    
    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_title: str = "SIGI Local API"
    api_description: str = "Sistema de Gestión de Incidencias con IA - API REST"
    api_version: str = "1.0.0"
    
    # Streamlit
    streamlit_port: int = 8501
    
    # Machine Learning
    ml_model_path: str = "data/models/"
    ml_cache_size: int = 100
    classification_threshold: float = 0.75
    sentiment_threshold: float = 0.6
    duplicate_threshold: float = 0.8
    
    # Categorías de clasificación
    categories: list = [
        "authentication",
        "performance", 
        "integration",
        "data",
        "ui_bug"
    ]
    
    # Niveles de prioridad
    priority_levels: list = [
        "critical",
        "high", 
        "medium",
        "low"
    ]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/sigi_local.log"
    
    # Seguridad
    secret_key: str = "sigi-local-secret-key-change-in-production"
    access_token_expire_minutes: int = 1440  # 24 horas
    
    class Config:
        env_file = "config/.env"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()

# Crear directorios necesarios
Path("data/database").mkdir(parents=True, exist_ok=True)
Path("data/models").mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(parents=True, exist_ok=True)
