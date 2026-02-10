from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from models import Datastream, Thing, Sensor, ObservedProperty, Observation
from schemas import DatastreamCreate, DatastreamUpdate, DatastreamResponse
from database import get_db

router = APIRouter()


## DATASTREAMS _______________________________________________________
@router.get("/", response_model=Dict[str, Any])
def get_datastreams(
    top: int = Query(100, alias="$top"),
    skip: int = Query(0, alias="$skip"),
    thing_id: Optional[str] = None,
    sensor_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Datastream)
    
    if thing_id:
        query = query.filter(Datastream.thing_id == thing_id)
    if sensor_id:
        query = query.filter(Datastream.sensor_id == sensor_id)
    
    total = query.count()
    datastreams = query.offset(skip).limit(top).all()
    return {"@iot.count": total, "value": datastreams}


@router.post("/", response_model=DatastreamResponse, status_code=201)
def create_datastream(ds_data: DatastreamCreate, db: Session = Depends(get_db)):
    # Vérifier que les entités liées existent
    if not db.query(Thing).filter(Thing.id == ds_data.thing_id).first():
        raise HTTPException(status_code=404, detail=f"Thing {ds_data.thing_id} not found")
    if not db.query(Sensor).filter(Sensor.id == ds_data.sensor_id).first():
        raise HTTPException(status_code=404, detail=f"Sensor {ds_data.sensor_id} not found")
    if not db.query(ObservedProperty).filter(ObservedProperty.id == ds_data.observed_property_id).first():
        raise HTTPException(status_code=404, detail=f"ObservedProperty {ds_data.observed_property_id} not found")

    db_ds = Datastream(
        name=ds_data.name,
        description=ds_data.description,
        observationType=ds_data.observationType,
        unitOfMeasurement=ds_data.unitOfMeasurement.dict(),
        thing_id=ds_data.thing_id,
        sensor_id=ds_data.sensor_id,
        observed_property_id=ds_data.observed_property_id
    )
    db.add(db_ds)
    db.commit()
    db.refresh(db_ds)
    return db_ds


@router.get("({datastream_id})", response_model=DatastreamResponse)
def get_datastream(datastream_id: str, db: Session = Depends(get_db)):
    datastream = db.query(Datastream).options(
        joinedload(Datastream.Thing),
        joinedload(Datastream.Sensor),
        joinedload(Datastream.ObservedProperty)
    ).filter(Datastream.id == datastream_id).first()
    
    if not datastream:
        raise HTTPException(status_code=404, detail="Datastream not found")
    return datastream


@router.patch("({datastream_id})", response_model=DatastreamResponse)
def update_datastream(
    datastream_id: str,
    ds_data: DatastreamUpdate,
    db: Session = Depends(get_db)
):
    datastream = db.query(Datastream).filter(Datastream.id == datastream_id).first()
    if not datastream:
        raise HTTPException(status_code=404, detail="Datastream not found")

    update_data = ds_data.dict(exclude_unset=True)

    # Convertir UnitOfMeasurement en dict pour JSONB
    if "unitOfMeasurement" in update_data:
        update_data["unitOfMeasurement"] = update_data["unitOfMeasurement"]

    for field, value in update_data.items():
        setattr(datastream, field, value)

    db.commit()
    db.refresh(datastream)
    return datastream


@router.delete("({datastream_id})", status_code=204)
def delete_datastream(datastream_id: str, db: Session = Depends(get_db)):
    datastream = db.query(Datastream).filter(Datastream.id == datastream_id).first()
    if not datastream:
        raise HTTPException(status_code=404, detail="Datastream not found")
    db.delete(datastream)
    db.commit()


# SensorThings : Observations d'un Datastream
@router.get("({datastream_id})/Observations", response_model=Dict[str, Any])
def get_datastream_observations(
    datastream_id: str,
    top: int = Query(100, alias="$top"),
    skip: int = Query(0, alias="$skip"),
    time_start: Optional[datetime] = None,
    time_end: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    datastream = db.query(Datastream).filter(Datastream.id == datastream_id).first()
    if not datastream:
        raise HTTPException(status_code=404, detail="Datastream not found")

    query = db.query(Observation).filter(Observation.datastream_id == datastream_id)

    if time_start:
        query = query.filter(Observation.phenomenonTime >= time_start)
    if time_end:
        query = query.filter(Observation.phenomenonTime <= time_end)

    total = query.count()
    observations = query.order_by(
        Observation.phenomenonTime.desc()
    ).offset(skip).limit(top).all()

    return {"@iot.count": total, "value": observations}


# SensorThings : Thing d'un Datastream
@router.get("({datastream_id})/Thing", response_model=Dict[str, Any])
def get_datastream_thing(datastream_id: str, db: Session = Depends(get_db)):
    datastream = db.query(Datastream).filter(Datastream.id == datastream_id).first()
    if not datastream:
        raise HTTPException(status_code=404, detail="Datastream not found")
    return datastream.Thing


# SensorThings : Sensor d'un Datastream
@router.get("({datastream_id})/Sensor", response_model=Dict[str, Any])
def get_datastream_sensor(datastream_id: str, db: Session = Depends(get_db)):
    datastream = db.query(Datastream).filter(Datastream.id == datastream_id).first()
    if not datastream:
        raise HTTPException(status_code=404, detail="Datastream not found")
    return datastream.Sensor


# SensorThings : ObservedProperty d'un Datastream
@router.get("({datastream_id})/ObservedProperty", response_model=Dict[str, Any])
def get_datastream_observed_property(datastream_id: str, db: Session = Depends(get_db)):
    datastream = db.query(Datastream).filter(Datastream.id == datastream_id).first()
    if not datastream:
        raise HTTPException(status_code=404, detail="Datastream not found")
    return datastream.ObservedProperty
