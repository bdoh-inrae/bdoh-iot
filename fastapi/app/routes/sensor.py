from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from models import Sensor
from schemas import SensorCreate, SensorUpdate, SensorResponse
from database import get_db

router = APIRouter()


## SENSORS ___________________________________________________________
@router.get("/", response_model=Dict[str, Any])
def get_sensors(
    top: int = Query(100, alias="$top"),
    skip: int = Query(0, alias="$skip"),
    db: Session = Depends(get_db)
):
    query = db.query(Sensor)
    total = query.count()
    sensors = query.offset(skip).limit(top).all()
    return {"@iot.count": total, "value": sensors}


@router.post("/", response_model=SensorResponse, status_code=201)
def create_sensor(sensor_data: SensorCreate, db: Session = Depends(get_db)):
    db_sensor = Sensor(
        name=sensor_data.name,
        description=sensor_data.description,
        encodingType=sensor_data.encodingType,
        metadata_=sensor_data.metadata  # ← metadata → metadata_
    )
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor


@router.get("({sensor_id})", response_model=SensorResponse)
def get_sensor(sensor_id: str, db: Session = Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.patch("({sensor_id})", response_model=SensorResponse)
def update_sensor(
    sensor_id: str,
    sensor_data: SensorUpdate,  # ← Pydantic, pas dict !
    db: Session = Depends(get_db)
):
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    update_data = sensor_data.dict(exclude_unset=True)

    # Gérer metadata → metadata_
    if "metadata" in update_data:
        sensor.metadata_ = update_data.pop("metadata")

    for field, value in update_data.items():
        setattr(sensor, field, value)

    db.commit()
    db.refresh(sensor)
    return sensor


@router.delete("({sensor_id})", status_code=204)
def delete_sensor(sensor_id: str, db: Session = Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    db.delete(sensor)
    db.commit()


# SensorThings : Datastreams d'un Sensor
@router.get("({sensor_id})/Datastreams", response_model=Dict[str, Any])
def get_sensor_datastreams(sensor_id: str, db: Session = Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return {"@iot.count": len(sensor.Datastreams), "value": sensor.Datastreams}
