from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## LOCATION ______________
class LocationBase(BaseModel):
    name: str
    description: Optional[str] = None
    encoding_type: str = "application/geo+json"
    location: Dict[str, Any]  # GeoJSON

class LocationCreate(LocationBase):
    """Schéma pour créer une Location"""
    id: Optional[str] = None
    thing_ids: Optional[List[str]] = Field(default_factory=list)

class LocationUpdate(BaseModel):
    """Mise à jour partielle"""
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[Dict[str, Any]] = None

class LocationResponse(LocationBase):
    """Schéma de réponse pour une Location"""
    id: str
    thing_ids: List[str] = Field(default_factory=list)
