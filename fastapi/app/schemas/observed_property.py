from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## OBSERVED PROPERTY ___________
class ObservedPropertyBase(BaseModel):
    name: str
    description: Optional[str] = None
    definition: str  # URI obligatoire dans SensorThings

    class Config:
        from_attributes = True
        populate_by_name = True

class ObservedPropertyCreate(ObservedPropertyBase):
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Temperature",
                "description": "Température de l'air",
                "definition": "http://qudt.org/vocab/unit/DEG_C"
            }
        }

class ObservedPropertyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[str] = None

class ObservedPropertyResponse(ObservedPropertyBase):
    id: str

    class Config:
        from_attributes = True
