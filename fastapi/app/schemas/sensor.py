from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## SENSOR ___________
class SensorBase(BaseModel):
    name: str
    description: Optional[str] = None
    encoding_type: str = "application/json"
    metadata: Optional[str] = None

class SensorCreate(SensorBase):
    """Schéma pour créer un Sensor"""
    id: Optional[str] = None

class SensorUpdate(BaseModel):
    """Mise à jour partielle"""
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[str] = None

class SensorResponse(SensorBase):
    """Schéma de réponse pour un Sensor"""
    id: str
    datastream_ids: List[str] = []
