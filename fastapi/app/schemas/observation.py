from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## OBSERBATION _______
class ObservationBase(BaseModel):
    phenomenonTime: datetime
    result: float
    resultTime: Optional[datetime] = None
    resultQuality: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    raw: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True

class ObservationCreate(ObservationBase):
    datastream_id: str
    feature_of_interest_id: Optional[str] = None

class ObservationUpdate(BaseModel):
    resultQuality: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None

class ObservationResponse(ObservationBase):
    id: int
    datastream_id: str
    feature_of_interest_id: Optional[str] = None

    class Config:
        from_attributes = True 
