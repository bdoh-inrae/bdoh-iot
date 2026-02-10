from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## FEATURE OF INTEREST _______________________
class FeatureOfInterestBase(BaseModel):
    name: str
    description: Optional[str] = None
    encodingType: str = "application/geo+json"  # ← camelCase cohérent
    feature: Dict[str, Any]  # GeoJSON

    class Config:
        from_attributes = True
        populate_by_name = True

class FeatureOfInterestCreate(FeatureOfInterestBase):
    # ← Plus d'id
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Parcelle agricole nord",
                "description": "Zone de culture blé",
                "encodingType": "application/geo+json",
                "feature": {
                    "type": "Polygon",
                    "coordinates": [[[2.35, 48.85], [2.36, 48.85], [2.36, 48.86], [2.35, 48.85]]]
                }
            }
        }

class FeatureOfInterestUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    feature: Optional[Dict[str, Any]] = None

class FeatureOfInterestResponse(FeatureOfInterestBase):
    id: str
    observation_ids: List[str] = []

    class Config:
        from_attributes = True
