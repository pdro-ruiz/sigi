
"""
Esquemas Pydantic para validación de datos
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CategoryEnum(str, Enum):
    authentication = "authentication"
    performance = "performance"
    integration = "integration"
    data = "data"
    ui_bug = "ui_bug"

class PriorityEnum(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class StatusEnum(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"

class UrgencyEnum(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

# Esquemas de Incident
class IncidentBase(BaseModel):
    title: str
    description: str
    priority: Optional[PriorityEnum] = PriorityEnum.medium

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[CategoryEnum] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None

class Incident(IncidentBase):
    id: int
    category: Optional[CategoryEnum] = None
    status: StatusEnum = StatusEnum.open
    sentiment_score: Optional[float] = None
    urgency_level: Optional[UrgencyEnum] = None
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    duplicate_of: Optional[int] = None

    class Config:
        from_attributes = True

# Esquemas de User
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "user"

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

# Esquemas de Response
class ResponseBase(BaseModel):
    message: str

class ResponseCreate(ResponseBase):
    incident_id: int
    user_id: int
    is_automated: bool = False

class Response(ResponseBase):
    id: int
    incident_id: int
    user_id: int
    is_automated: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Esquemas de ML Prediction
class PredictionBase(BaseModel):
    model_name: str
    prediction_type: str
    prediction_value: str
    confidence_score: Optional[float] = None

class PredictionCreate(PredictionBase):
    incident_id: int

class MLPrediction(PredictionBase):
    id: int
    incident_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Esquemas de análisis IA
class ClassificationResult(BaseModel):
    category: CategoryEnum
    confidence: float

class SentimentResult(BaseModel):
    sentiment: str  # positive, neutral, negative
    score: float

class UrgencyResult(BaseModel):
    urgency: UrgencyEnum
    confidence: float

class DuplicateCandidate(BaseModel):
    incident_id: int
    title: str
    similarity_score: float

class SuggestedResponse(BaseModel):
    template_id: int
    content: str
    relevance_score: float

class AnalysisResult(BaseModel):
    incident_id: int
    classification: ClassificationResult
    sentiment: SentimentResult
    urgency: UrgencyResult
    duplicates: List[DuplicateCandidate]
    suggested_responses: List[SuggestedResponse]

# Esquemas para dashboard
class DashboardStats(BaseModel):
    total_incidents: int
    open_incidents: int
    resolved_incidents: int
    average_resolution_time: float
    incidents_by_category: dict
    incidents_by_priority: dict
    sentiment_distribution: dict

class FeedbackCreate(BaseModel):
    incident_id: int
    prediction_id: int
    user_id: int
    feedback_type: str  # correct/incorrect
    correct_value: Optional[str] = None
