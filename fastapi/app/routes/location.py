from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, Optional
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from datetime import datetime
import uuid

from models import Location, Thing
from schemas import LocationCreate, LocationUpdate, LocationResponse
from database import get_db

router = APIRouter()


## LOCATIONS __________________________________________________________
@router.get("/", response_model=Dict[str, Any])
def get_locations(
    top: int = Query(100, alias="$top"),
    skip: int = Query(0, alias="$skip"),
    db: Session = Depends(get_db)
):
    query = db.query(Location)
    total = query.count()
    locations = query.offset(skip).limit(top).all()
    return {"@iot.count": total, "value": locations}


@router.post("/", response_model=LocationResponse, status_code=201)
def create_location(location_data: LocationCreate, db: Session = Depends(get_db)):
    try:
        geom = from_shape(shape(location_data.location), srid=4326)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid GeoJSON geometry")
    
    db_location = Location(
        name=location_data.name,
        description=location_data.description,
        encodingType=location_data.encodingType,
        location=geom
    )

    if location_data.thing_ids:
        things = db.query(Thing).filter(
            Thing.id.in_(location_data.thing_ids)
        ).all()
        if len(things) != len(location_data.thing_ids):
            raise HTTPException(status_code=404, detail="One or more Things not found")
        db_location.Things = things

    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


@router.get("({location_id})", response_model=LocationResponse)
def get_location(location_id: str, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.patch("({location_id})", response_model=LocationResponse)
def update_location(
    location_id: str,
    location_data: LocationUpdate,
    db: Session = Depends(get_db)
):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    update_data = location_data.dict(exclude_unset=True)
    
    # Convertir GeoJSON si fourni
    if "location" in update_data:
        try:
            update_data["location"] = from_shape(shape(update_data["location"]), srid=4326)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid GeoJSON geometry")
    
    for field, value in update_data.items():
        setattr(location, field, value)
    
    db.commit()
    db.refresh(location)
    return location


@router.delete("({location_id})", status_code=204)
def delete_location(location_id: str, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(location)
    db.commit()


# SensorThings : Things d'une Location
@router.get("({location_id})/Things", response_model=Dict[str, Any])
def get_location_things(location_id: str, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"@iot.count": len(location.Things), "value": location.Things}
