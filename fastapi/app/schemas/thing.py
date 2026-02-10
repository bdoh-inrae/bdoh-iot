from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## THING ____________
class ThingBase(BaseModel):
    name: str
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
        populate_by_name = True

class ThingCreate(ThingBase):
    id: Optional[str] = None
    location_ids: Optional[List[str]] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Weather Station Paris",
                "description": "Station météo officielle",
                "properties": {"owner": "Météo France"},
                "location_ids": ["loc-123"]
            }
        }

class ThingUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    location_ids: Optional[List[str]] = None  # ← Permet de mettre à jour les locations

class ThingResponse(ThingBase):
    id: str
    location_ids: List[str] = Field(default_factory=list)
    datastream_ids: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True
