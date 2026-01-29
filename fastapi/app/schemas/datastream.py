from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## DATASTREAM _____________
class DatastreamBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    observation_type: str = "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"
    unit_of_measurement: Dict[str, str] = Field(
        ...,
        description="e.g., {'name': 'Celsius', 'symbol': '°C', 'definition': 'http://...'}"
    )

class DatastreamCreate(DatastreamBase):
    """Schéma pour créer un Datastream"""
    id: Optional[str] = None
    thing_id: str
    sensor_id: str
    observed_property_id: str

class DatastreamUpdate(BaseModel):
    """Mise à jour partielle"""
    name: Optional[str] = None
    description: Optional[str] = None
    unit_of_measurement: Optional[Dict[str, str]] = None

class DatastreamResponse(DatastreamBase):
    """Schéma de réponse pour un Datastream"""
    id: str
    thing_id: str
    sensor_id: str
    observed_property_id: str
    observation_ids: List[str] = Field(default_factory=list)
