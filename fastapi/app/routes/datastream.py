from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Datastream
from app.schemas import DatastreamCreate, DatastreamResponse
from app.database import get_db

router = APIRouter()


## DATASTREAMS _______________________________________________________
@app.get("/v1.0/Datastreams", response_model=Dict[str, Any])
def get_datastreams(skip: int=0, limit: int=100, db: Session=Depends(get_db)):
    datastreams = db.query(Datastream).offset(skip).limit(limit).all()
    return {"@iot.count": len(datastreams), "value": datastreams}

@app.post("/v1.0/Datastreams", response_model=DatastreamResponse)
def create_datastream(ds_data: DatastreamCreate, db: Session = Depends(get_db)):
    existing = db.query(Datastream).filter(Datastream.id == ds_data.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Datastream already exists")
    
    # Extract IDs from STA nested format
    data_dict = ds_data.dict()
    
    # Convert STA format to model fields
    model_data = {
        "id": data_dict.get("id"),
        "name": data_dict.get("name"),
        "description": data_dict.get("description"),
        "observationType": data_dict.get("observationType"),
        "unitOfMeasurement": data_dict.get("unitOfMeasurement"),
        # Extract IDs from nested dicts
        "thing_id": data_dict.get("Thing", {}).get("@iot.id") if data_dict.get("Thing") else None,
        "sensor_id": data_dict.get("Sensor", {}).get("@iot.id") if data_dict.get("Sensor") else None,
        "observed_property_id": data_dict.get("ObservedProperty", {}).get("@iot.id") if data_dict.get("ObservedProperty") else None,
    }
    
    # Validate required foreign keys
    if not model_data["thing_id"]:
        raise HTTPException(status_code=400, detail="Thing ID is required")
    if not model_data["sensor_id"]:
        raise HTTPException(status_code=400, detail="Sensor ID is required")
    if not model_data["observed_property_id"]:
        raise HTTPException(status_code=400, detail="ObservedProperty ID is required")
    
    # Check if referenced entities exist
    thing = db.query(Thing).filter(Thing.id == model_data["thing_id"]).first()
    if not thing:
        raise HTTPException(status_code=404, detail=f"Thing with id {model_data['thing_id']} not found")
    
    sensor = db.query(Sensor).filter(Sensor.id == model_data["sensor_id"]).first()
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor with id {model_data['sensor_id']} not found")
    
    observed_property = db.query(ObservedProperty).filter(ObservedProperty.id == model_data["observed_property_id"]).first()
    if not observed_property:
        raise HTTPException(status_code=404, detail=f"ObservedProperty with id {model_data['observed_property_id']} not found")
    
    db_ds = Datastream(**model_data)
    db.add(db_ds)
    db.commit()
    db.refresh(db_ds)
    return db_ds

@app.get("/v1.0/Datastreams({datastream_id})", response_model=DatastreamResponse)
def get_datastream(datastream_id: str, db: Session = Depends(get_db)):
    datastream = db.query(Datastream).options(
        joinedload(Datastream.Thing),
        joinedload(Datastream.Sensor),
        joinedload(Datastream.ObservedProperty)
    ).filter(Datastream.id == datastream_id).first()
    
    if not datastream:
        raise HTTPException(status_code=404, detail="Datastream not found")
    
    return datastream

@app.patch("/v1.0/Datastreams({datastream_id})", response_model=DatastreamResponse)
def update_datastream(datastream_id: str, ds_update: dict, db: Session=Depends(get_db)):
    datastream = db.query(Datastream).filter(Datastream.id == datastream_id).first()
    if not datastream:
        raise HTTPException(status_code=404, detail="Datastream not found")
    
    for field, value in ds_update.items():
        if hasattr(datastream, field):
            setattr(datastream, field, value)
    
    db.commit()
    db.refresh(datastream)
    return datastream

@app.delete("/v1.0/Datastreams({datastream_id})")
def delete_datastream(datastream_id: str, db: Session=Depends(get_db)):
    datastream = db.query(Datastream).filter(Datastream.id == datastream_id).first()
    if not datastream:
        raise HTTPException(status_code=404, detail="Datastream not found")
    
    db.delete(datastream)
    db.commit()
    return {"message": "Datastream deleted"}

