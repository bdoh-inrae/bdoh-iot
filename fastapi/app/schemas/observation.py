from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## OBSERBATION _______
class ObservationBase(BaseModel):
    phenomenon_time: datetime
    result: float
    result_time: Optional[datetime] = None
    result_quality: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    raw: Optional[Dict[str, Any]] = Field(
        None,
        description="Données brutes du capteur"
    )

class ObservationCreate(ObservationBase):
    """Schéma pour créer une Observation"""
    datastream_id: str
    feature_of_interest_id: Optional[str] = None

class ObservationUpdate(BaseModel):
    """Mise à jour partielle (rarement utilisé)"""
    result_quality: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None

class ObservationResponse(ObservationBase):
    """Schéma de réponse pour une Observation"""
    id: int
    datastream_id: str
    feature_of_interest_id: Optional[str] = None

