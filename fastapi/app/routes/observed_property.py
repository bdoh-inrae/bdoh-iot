from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import ObservedProperty
from app.schemas import ObservedPropertyCreate, ObservedPropertyResponse
from app.database import get_db

router = APIRouter()


## OBSERVED PROPERTIES _______________________________________________
@app.get("/v1.0/ObservedProperties", response_model=Dict[str, Any])
def get_observed_properties(skip: int=0, limit: int=100, db: Session=Depends(get_db)):
    props = db.query(ObservedProperty).offset(skip).limit(limit).all()
    return {"@iot.count": len(props), "value": props}

@app.post("/v1.0/ObservedProperties", response_model=ObservedPropertyResponse)
def create_observed_property(prop_data: ObservedPropertyCreate, db: Session=Depends(get_db)):
    existing = db.query(ObservedProperty).filter(ObservedProperty.id == prop_data.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="ObservedProperty already exists")
    
    db_prop = ObservedProperty(**prop_data.dict())
    db.add(db_prop)
    db.commit()
    db.refresh(db_prop)
    return db_prop

# ... add GET, PATCH, DELETE for ObservedProperty
