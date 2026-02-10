from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from models import ObservedProperty
from schemas import ObservedPropertyCreate, ObservedPropertyUpdate, ObservedPropertyResponse
from database import get_db

router = APIRouter()


## OBSERVED PROPERTIES _______________________________________________
@router.get("/", response_model=Dict[str, Any])
def get_observed_properties(
    top: int = Query(100, alias="$top"),
    skip: int = Query(0, alias="$skip"),
    db: Session = Depends(get_db)
):
    query = db.query(ObservedProperty)
    total = query.count()  # ← Vrai total
    props = query.offset(skip).limit(top).all()
    return {"@iot.count": total, "value": props}


@router.post("/", response_model=ObservedPropertyResponse, status_code=201)
def create_observed_property(prop_data: ObservedPropertyCreate, db: Session = Depends(get_db)):
    db_prop = ObservedProperty(
        name=prop_data.name,
        description=prop_data.description,
        definition=prop_data.definition
    )
    db.add(db_prop)
    db.commit()
    db.refresh(db_prop)
    return db_prop


@router.get("({prop_id})", response_model=ObservedPropertyResponse)
def get_observed_property(prop_id: str, db: Session = Depends(get_db)):
    prop = db.query(ObservedProperty).filter(ObservedProperty.id == prop_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="ObservedProperty not found")
    return prop


@router.patch("({prop_id})", response_model=ObservedPropertyResponse)
def update_observed_property(
    prop_id: str,
    prop_data: ObservedPropertyUpdate,
    db: Session = Depends(get_db)
):
    prop = db.query(ObservedProperty).filter(ObservedProperty.id == prop_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="ObservedProperty not found")
    
    for field, value in prop_data.dict(exclude_unset=True).items():
        setattr(prop, field, value)
    
    db.commit()
    db.refresh(prop)
    return prop


@router.delete("({prop_id})", status_code=204)
def delete_observed_property(prop_id: str, db: Session = Depends(get_db)):
    prop = db.query(ObservedProperty).filter(ObservedProperty.id == prop_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="ObservedProperty not found")
    db.delete(prop)
    db.commit()


# SensorThings : Datastreams d'une ObservedProperty
@router.get("({prop_id})/Datastreams", response_model=Dict[str, Any])
def get_observed_property_datastreams(prop_id: str, db: Session = Depends(get_db)):
    prop = db.query(ObservedProperty).filter(ObservedProperty.id == prop_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="ObservedProperty not found")
    return {"@iot.count": len(prop.Datastreams), "value": prop.Datastreams}
