from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## FEATURE OF INTEREST _______________________
class FeatureOfInterestBase(BaseModel):
    name: str
    description: Optional[str] = None
    encoding_type: str = "application/geo+json"
    feature: Dict[str, Any]  # GeoJSON

class FeatureOfInterestCreate(FeatureOfInterestBase):
    """Schéma pour créer une FeatureOfInterest"""
    id: Optional[str] = None

class FeatureOfInterestUpdate(BaseModel):
    """Mise à jour partielle"""
    name: Optional[str] = None
    description: Optional[str] = None
    feature: Optional[Dict[str, Any]] = None

class FeatureOfInterestResponse(FeatureOfInterestBase):
    """Schéma de réponse pour une FeatureOfInterest"""
    id: str
    observation_ids: List[str] = []
