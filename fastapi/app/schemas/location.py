from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any, List
from datetime import datetime


## LOCATION ______________
class LocationBase(BaseModel):
    name: str
    description: Optional[str] = None
    encodingType: str = "application/geo+json"
    location: Dict[str, Any]  # GeoJSON ex: {"type": "Point", "coordinates": [lon, lat]}

    class Config:
        from_attributes = True
        populate_by_name = True

class LocationCreate(LocationBase):
    thing_ids: Optional[List[str]] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Station Paris",
                "encodingType": "application/geo+json",
                "location": {
                    "type": "Point",
                    "coordinates": [2.3522, 48.8566]
                },
                "thing_ids": []
            }
        }
    
class LocationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[Dict[str, Any]] = None

class LocationResponse(LocationBase):
    id: str
    thing_ids: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True
