from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from datetime import datetime
import uuid

from models import FeatureOfInterest
from schemas import FeatureOfInterestCreate, FeatureOfInterestUpdate, FeatureOfInterestResponse
from database import get_db

router = APIRouter()


## FEATURES OF INTEREST ______________________________________________
@router.get("/", response_model=Dict[str, Any])
def get_features_of_interest(
    top: int = Query(100, alias="$top"),
    skip: int = Query(0, alias="$skip"),
    db: Session = Depends(get_db)
):
    query = db.query(FeatureOfInterest)
    total = query.count()
    fois = query.offset(skip).limit(top).all()
    return {"@iot.count": total, "value": fois}


@router.post("/", response_model=FeatureOfInterestResponse, status_code=201)
def create_feature_of_interest(foi_data: FeatureOfInterestCreate, db: Session = Depends(get_db)):
    # Convertir GeoJSON → PostGIS
    try:
        geom = from_shape(shape(foi_data.feature), srid=4326)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid GeoJSON geometry")

    db_foi = FeatureOfInterest(
        name=foi_data.name,
        description=foi_data.description,
        encodingType=foi_data.encodingType,
        feature=geom
    )
    db.add(db_foi)
    db.commit()
    db.refresh(db_foi)
    return db_foi


@router.get("({foi_id})", response_model=FeatureOfInterestResponse)
def get_feature_of_interest(foi_id: str, db: Session = Depends(get_db)):
    foi = db.query(FeatureOfInterest).filter(FeatureOfInterest.id == foi_id).first()
    if not foi:
        raise HTTPException(status_code=404, detail="FeatureOfInterest not found")
    return foi


@router.patch("({foi_id})", response_model=FeatureOfInterestResponse)
def update_feature_of_interest(
    foi_id: str,
    foi_data: FeatureOfInterestUpdate,
    db: Session = Depends(get_db)
):
    foi = db.query(FeatureOfInterest).filter(FeatureOfInterest.id == foi_id).first()
    if not foi:
        raise HTTPException(status_code=404, detail="FeatureOfInterest not found")

    update_data = foi_data.dict(exclude_unset=True)

    # Convertir GeoJSON si fourni
    if "feature" in update_data:
        try:
            update_data["feature"] = from_shape(shape(update_data["feature"]), srid=4326)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid GeoJSON geometry")

    for field, value in update_data.items():
        setattr(foi, field, value)

    db.commit()
    db.refresh(foi)
    return foi


@router.delete("({foi_id})", status_code=204)
def delete_feature_of_interest(foi_id: str, db: Session = Depends(get_db)):
    foi = db.query(FeatureOfInterest).filter(FeatureOfInterest.id == foi_id).first()
    if not foi:
        raise HTTPException(status_code=404, detail="FeatureOfInterest not found")
    db.delete(foi)
    db.commit()


# SensorThings : Observations d'une FeatureOfInterest
@router.get("({foi_id})/Observations", response_model=Dict[str, Any])
def get_foi_observations(
    foi_id: str,
    top: int = Query(100, alias="$top"),
    skip: int = Query(0, alias="$skip"),
    db: Session = Depends(get_db)
):
    foi = db.query(FeatureOfInterest).filter(FeatureOfInterest.id == foi_id).first()
    if not foi:
        raise HTTPException(status_code=404, detail="FeatureOfInterest not found")
    
    total = len(foi.Observations)
    observations = foi.Observations[skip:skip+top]
    return {"@iot.count": total, "value": observations}
