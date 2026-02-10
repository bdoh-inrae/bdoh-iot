from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from models import Thing
from schemas import ThingCreate, ThingUpdate, ThingResponse
from database import get_db

router = APIRouter()


## THINGS ____________________________________________________________
@router.get("/", response_model=Dict[str, Any])
def get_things(
    top: int = Query(100, alias="$top"),
    skip: int = Query(0, alias="$skip"),
    db: Session = Depends(get_db)
):
    query = db.query(Thing)
    total = query.count()
    things = query.offset(skip).limit(top).all()
    return {"@iot.count": total, "value": things}


@router.post("/", response_model=ThingResponse, status_code=201)
def create_thing(thing_data: ThingCreate, db: Session = Depends(get_db)):
    db_thing = Thing(
        name=thing_data.name,
        description=thing_data.description,
        properties=thing_data.properties
    )

    if thing_data.location_ids:
        locations = db.query(Location).filter(
            Location.id.in_(thing_data.location_ids)
        ).all()
        if len(locations) != len(thing_data.location_ids):
            raise HTTPException(status_code=404, detail="One or more Locations not found")
        db_thing.Locations = locations

    db.add(db_thing)
    db.commit()
    db.refresh(db_thing)
    return db_thing


@router.get("({thing_id})", response_model=ThingResponse)
def get_thing(thing_id: str, db: Session = Depends(get_db)):
    thing = db.query(Thing).filter(Thing.id == thing_id).first()
    if not thing:
        raise HTTPException(status_code=404, detail="Thing not found")
    return thing


@router.patch("({thing_id})", response_model=ThingResponse)
def update_thing(
    thing_id: str,
    thing_data: ThingUpdate,  # ← Pydantic, pas dict !
    db: Session = Depends(get_db)
):
    thing = db.query(Thing).filter(Thing.id == thing_id).first()
    if not thing:
        raise HTTPException(status_code=404, detail="Thing not found")

    update_data = thing_data.dict(exclude_unset=True)

    # Gérer location_ids séparément
    if "location_ids" in update_data:
        locations = db.query(Location).filter(
            Location.id.in_(update_data.pop("location_ids"))
        ).all()
        thing.Locations = locations

    for field, value in update_data.items():
        setattr(thing, field, value)

    db.commit()
    db.refresh(thing)
    return thing


@router.delete("({thing_id})", status_code=204)
def delete_thing(thing_id: str, db: Session = Depends(get_db)):
    thing = db.query(Thing).filter(Thing.id == thing_id).first()
    if not thing:
        raise HTTPException(status_code=404, detail="Thing not found")
    db.delete(thing)
    db.commit()


# SensorThings : Locations d'un Thing
@router.get("({thing_id})/Locations", response_model=Dict[str, Any])
def get_thing_locations(thing_id: str, db: Session = Depends(get_db)):
    thing = db.query(Thing).filter(Thing.id == thing_id).first()
    if not thing:
        raise HTTPException(status_code=404, detail="Thing not found")
    return {"@iot.count": len(thing.Locations), "value": thing.Locations}


# SensorThings : Datastreams d'un Thing
@router.get("({thing_id})/Datastreams", response_model=Dict[str, Any])
def get_thing_datastreams(thing_id: str, db: Session = Depends(get_db)):
    thing = db.query(Thing).filter(Thing.id == thing_id).first()
    if not thing:
        raise HTTPException(status_code=404, detail="Thing not found")
    return {"@iot.count": len(thing.Datastreams), "value": thing.Datastreams}
