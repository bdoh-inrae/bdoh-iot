from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Observation
from app.schemas import ObservationCreate, ObservationResponse
from app.database import get_db

router = APIRouter()


## OBSERVATIONS ______________________________________________________
@app.get("/v1.0/Observations", response_model=Dict[str, Any])
def get_observations(
    datastream_id: Optional[str] = None,
    skip: int=0,
    limit: int=100,
    db: Session=Depends(get_db)
):
    query = db.query(Observation)
    if datastream_id:
        query = query.filter(Observation.datastream_id == datastream_id)
    
    observations = query.order_by(Observation.time.desc()).offset(skip).limit(limit).all()
    return {"@iot.count": query.count(), "value": observations}

@app.post("/v1.0/Observations", response_model=ObservationResponse)
def create_observation(obs_data: ObservationCreate, db: Session=Depends(get_db)):
    db_obs = Observation(**obs_data.dict())
    db.add(db_obs)
    db.commit()
    db.refresh(db_obs)
    return db_obs

@app.get("/v1.0/Observations({observation_id})", response_model=ObservationResponse)
def get_observation(observation_id: int, db: Session=Depends(get_db)):
    observation = db.query(Observation).filter(Observation.id == observation_id).first()
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    return observation

@app.delete("/v1.0/Observations({observation_id})")
def delete_observation(observation_id: int, db: Session=Depends(get_db)):
    observation = db.query(Observation).filter(Observation.id == observation_id).first()
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    db.delete(observation)
    db.commit()
    return {"message": "Observation deleted"}

