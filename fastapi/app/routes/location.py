from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Location
from app.schemas import LocationCreate, LocationResponse
from app.database import get_db

router = APIRouter()


## LOCATIONS __________________________________________________________
@app.get("/v1.0/Locations", response_model=Dict[str, Any])
def get_locations(skip: int=0, limit: int=100, db: Session=Depends(get_db)):
    locations = db.query(Location).offset(skip).limit(limit).all()
    return {"@iot.count": len(locations), "value": locations}

@app.post("/v1.0/Locations", response_model=LocationResponse)
def create_location(location_data: LocationCreate, db: Session=Depends(get_db)):
    existing = db.query(Location).filter(Location.id == location_data.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Location already exists")
    
    db_location = Location(**location_data.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@app.get("/v1.0/Locations({location_id})", response_model=LocationResponse)
def get_location(location_id: str, db: Session=Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

# ... add PATCH and DELETE for Location too
