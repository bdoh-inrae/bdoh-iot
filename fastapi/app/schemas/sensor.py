from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## SENSOR ___________
class SensorBase(BaseModel):
    name: str
    description: Optional[str] = None
    encodingType: str = "application/json"
    metadata: Optional[str] = Field(None, alias="metadata_")  # ← Gère le underscore

    class Config:
        from_attributes = True
        populate_by_name = True

class SensorCreate(SensorBase):
    # ← Plus d'id
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Capteur température DHT22",
                "description": "Capteur température et humidité",
                "encodingType": "application/json",
                "metadata": "https://www.example.com/sensors/dht22.pdf"
            }
        }

class SensorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[str] = None

class SensorResponse(SensorBase):
    id: str
    datastream_ids: List[str] = []

    class Config:
        from_attributes = True
        populate_by_name = True
