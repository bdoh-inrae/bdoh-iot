from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## THING ____________
class ThingBase(BaseModel):
    name: str
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

class ThingCreate(ThingBase):
    """Schéma pour créer un Thing"""
    id: Optional[str] = None
    location_ids: Optional[List[str]] = Field(default_factory=list)  # IDs simples
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Weather Station Paris",
                "description": "Station météo officielle",
                "properties": {"owner": "Météo France"},
                "location_ids": ["loc-123", "loc-456"]
            }
        }

class ThingUpdate(BaseModel):
    """Schéma pour mettre à jour un Thing partiellement"""
    name: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

class ThingResponse(ThingBase):
    """Schéma de réponse pour un Thing"""
    id: str
    location_ids: List[str] = Field(default_factory=list)
    datastream_ids: List[str] = Field(default_factory=list)
