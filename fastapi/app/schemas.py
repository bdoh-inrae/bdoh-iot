from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## THING _____________________________________________________________
class ThingBase(BaseModel):
    name: str
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

class ThingCreate(ThingBase):
    id: Optional[str] = None
    Locations: Optional[List[Dict[str, str]]] = []  # [{"@iot.id": "loc1"}]

class ThingResponse(ThingBase):
    id: str
    Locations: Optional[List[Dict]] = []
    Datastreams: Optional[List[Dict]] = []
    
    class Config:
        from_attributes = True

        
## LOCATION __________________________________________________________
class LocationBase(BaseModel):
    name: str
    description: Optional[str] = None
    encodingType: str = "application/geo+json"
    location: Dict[str, Any]  # GeoJSON

class LocationCreate(LocationBase):
    id: Optional[str] = None

class LocationResponse(LocationBase):
    id: str
    Things: Optional[List[Dict]] = []
    
    class Config:
        from_attributes = True


## SENSOR ____________________________________________________________
class SensorBase(BaseModel):
    name: str
    description: Optional[str] = None
    encodingType: str = "application/json"  # STA required field
    metadata: Optional[str] = None  # STA field for sensor metadata

class SensorCreate(SensorBase):
    id: Optional[str] = None

class SensorResponse(SensorBase):
    id: str
    Datastreams_link: Optional[str] = None
    
    class Config:
        from_attributes = True

        
## OBSERVEDPROPERTY __________________________________________________
class ObservedPropertyBase(BaseModel):
    name: str
    description: Optional[str] = None
    definition: str  # URI

class ObservedPropertyCreate(ObservedPropertyBase):
    id: Optional[str] = None

class ObservedPropertyResponse(ObservedPropertyBase):
    id: str
    
    class Config:
        from_attributes = True


## DATASTREAM ________________________________________________________
class DatastreamBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    observationType: str = "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"
    unitOfMeasurement: Dict[str, str]  # e.g., {"name": "Celsius", "symbol": "°C"}

class DatastreamCreate(DatastreamBase):
    id: Optional[str] = None
    Thing: Dict[str, str]  # {"@iot.id": "thing_id"}
    Sensor: Dict[str, str]  # {"@iot.id": "sensor_id"}
    ObservedProperty: Dict[str, str]  # {"@iot.id": "observed_property_id"} - REQUIRED

class DatastreamResponse(DatastreamBase):
    id: str
    Thing: Optional[Dict[str, str]] = None
    Sensor: Optional[Dict[str, str]] = None
    ObservedProperty: Optional[Dict[str, str]] = None
    
    class Config:
        from_attributes = True


## OBSERVATION _______________________________________________________
class ObservationBase(BaseModel):
    phenomenonTime: datetime
    result: float
    resultTime: Optional[datetime] = None
    resultQuality: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None

class ObservationCreate(ObservationBase):
    Datastream: Dict[str, str]  # {"@iot.id": "datastream_id"}
    FeatureOfInterest: Optional[Dict[str, str]] = None  # {"@iot.id": "foi_id"}

class ObservationResponse(ObservationBase):
    id: int
    Datastream: Optional[Dict[str, str]] = None
    FeatureOfInterest: Optional[Dict[str, str]] = None
    
    class Config:
        from_attributes = True


## FEATUREOFINTEREST _________________________________________________
class FeatureOfInterestBase(BaseModel):
    name: str
    description: Optional[str] = None
    encodingType: str = "application/geo+json"
    feature: Dict[str, Any]  # GeoJSON

class FeatureOfInterestCreate(FeatureOfInterestBase):
    id: Optional[str] = None

class FeatureOfInterestResponse(FeatureOfInterestBase):
    id: str
    
    class Config:
        from_attributes = True
