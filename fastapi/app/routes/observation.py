from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from models import Observation
from schemas import ObservationCreate, ObservationUpdate, ObservationResponse
from database import get_db

router = APIRouter()


## OBSERVATIONS ______________________________________________________
@router.get("/", response_model=Dict[str, Any])
def get_observations(
    # Vos filtres métier
    datastream_id: Optional[str] = None,
    # OData de base
    top: int = Query(100, alias="$top"),
    skip: int = Query(0, alias="$skip"),
    orderby: str = Query("phenomenonTime desc", alias="$orderby"),
    # Filtres temporels utiles pour votre cas
    time_start: Optional[datetime] = None,
    time_end: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Observation)
    
    if datastream_id:
        query = query.filter(Observation.datastream_id == datastream_id)
    if time_start:
        query = query.filter(Observation.phenomenonTime >= time_start)
    if time_end:
        query = query.filter(Observation.phenomenonTime <= time_end)
    
    # Tri
    if "desc" in orderby:
        query = query.order_by(Observation.phenomenonTime.desc())
    else:
        query = query.order_by(Observation.phenomenonTime.asc())
    
    total = query.count()
    observations = query.offset(skip).limit(top).all()
    
    return {
        "@iot.count": total,
        "value": observations
    }

@router.post("/", response_model=ObservationResponse)
def create_observation(obs_data: ObservationCreate, db: Session = Depends(get_db)):
    db_obs = Observation(**obs_data.dict())
    db.add(db_obs)
    db.commit()
    db.refresh(db_obs)
    return db_obs

@router.get("({observation_id})", response_model=ObservationResponse)
def get_observation(observation_id: int, db: Session = Depends(get_db)):
    observation = db.query(Observation).filter(Observation.id == observation_id).first()
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    return observation

@router.patch("({observation_id})", response_model=ObservationResponse)
def update_observation(
    observation_id: int,
    obs_data: ObservationUpdate,
    db: Session = Depends(get_db)
):
    observation = db.query(Observation).filter(Observation.id == observation_id).first()
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    # Mise à jour uniquement des champs fournis
    update_data = obs_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(observation, field, value)
    
    db.commit()
    db.refresh(observation)
    return observation

@router.delete("({observation_id})")
def delete_observation(observation_id: int, db: Session = Depends(get_db)):
    observation = db.query(Observation).filter(Observation.id == observation_id).first()
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    db.delete(observation)
    db.commit()
    return {"message": "Observation deleted"}

# Route SensorThings : observations d'un datastream spécifique
@router.get("/Datastreams({datastream_id})/Observations", response_model=Dict[str, Any])
def get_observations_by_datastream(
    datastream_id: str,
    top: int = Query(100, alias="$top"),
    skip: int = Query(0, alias="$skip"),
    time_start: Optional[datetime] = None,
    time_end: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Observation).filter(Observation.datastream_id == datastream_id)
    
    if time_start:
        query = query.filter(Observation.phenomenonTime >= time_start)
    if time_end:
        query = query.filter(Observation.phenomenonTime <= time_end)
    
    total = query.count()
    observations = query.offset(skip).limit(top).order_by(Observation.phenomenonTime.desc()).all()
    
    return {
        "@iot.count": total,
        "value": observations
    }
