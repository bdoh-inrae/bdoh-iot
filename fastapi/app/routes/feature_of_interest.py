from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import FeatureOfInterest
from app.schemas import FeatureOfInterestCreate, FeatureOfInterestResponse
from app.database import get_db

router = APIRouter()


## FEATURES OF INTEREST ______________________________________________
@app.get("/v1.0/FeaturesOfInterest", response_model=Dict[str, Any])
def get_features_of_interest(skip: int=0, limit: int=100, db: Session=Depends(get_db)):
    fois = db.query(FeatureOfInterest).offset(skip).limit(limit).all()
    return {"@iot.count": len(fois), "value": fois}

@app.post("/v1.0/FeaturesOfInterest", response_model=FeatureOfInterestResponse)
def create_feature_of_interest(foi_data: FeatureOfInterestCreate, db: Session=Depends(get_db)):
    existing = db.query(FeatureOfInterest).filter(FeatureOfInterest.id == foi_data.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="FeatureOfInterest already exists")
    
    db_foi = FeatureOfInterest(**foi_data.dict())
    db.add(db_foi)
    db.commit()
    db.refresh(db_foi)
    return db_foi

# ... add GET, PATCH, DELETE for FeatureOfInterest
