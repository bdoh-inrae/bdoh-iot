from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class UnitOfMeasurement(BaseModel):
    """Conforme SensorThings"""
    name: str
    symbol: str
    definition: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Celsius",
                "symbol": "°C",
                "definition": "http://qudt.org/vocab/unit/DEG_C"
            }
        }


## DATASTREAM _____________
class DatastreamBase(BaseModel):
    name: str
    description: Optional[str] = None
    observationType: str = "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"
    unitOfMeasurement: UnitOfMeasurement

    class Config:
        from_attributes = True
        populate_by_name = True

class DatastreamCreate(DatastreamBase):
    # ← Plus d'id
    thing_id: str
    sensor_id: str
    observed_property_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Température air Paris",
                "description": "Mesure température air station Paris",
                "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
                "unitOfMeasurement": {
                    "name": "Celsius",
                    "symbol": "°C",
                    "definition": "http://qudt.org/vocab/unit/DEG_C"
                },
                "thing_id": "uuid-du-thing",
                "sensor_id": "uuid-du-sensor",
                "observed_property_id": "uuid-de-lobservedproperty"
            }
        }

class DatastreamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unitOfMeasurement: Optional[UnitOfMeasurement] = None
    observationType: Optional[str] = None

class DatastreamResponse(DatastreamBase):
    id: str
    thing_id: str
    sensor_id: str
    observed_property_id: str

    class Config:
        from_attributes = True
