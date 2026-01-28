from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import engine, SessionLocal

from app.models import Thing, Sensor, Datastream, Base, Observation, ObservedProperty, Location, FeatureOfInterest

from app.schemas import (
    ThingCreate, ThingResponse,
    SensorCreate, SensorResponse, 
    DatastreamCreate, DatastreamResponse,
    ObservationCreate, ObservationResponse,
    LocationCreate, LocationResponse,
    ObservedPropertyCreate, ObservedPropertyResponse,
    FeatureOfInterestCreate, FeatureOfInterestResponse
)

from app import mqtt_listener
from typing import Optional, Dict, Any

from sqlalchemy import event

from app.database_init import setup_database
import threading
import logging

Base.metadata.create_all(bind=engine)


## DB SETUP __________________________________________________________
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create all tables
Base.metadata.create_all(bind=engine)

# Setup TimescaleDB features
try:
    setup_database()
    logger.info("Database setup completed successfully")
except Exception as e:
    logger.warning(f"Database setup had issues (might already be initialized): {e}")


## PARAM __________
app = FastAPI(title="BDOH IoT API - SensorThings Compliant")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        
## THINGS ____________________________________________________________
@app.get("/v1.0/Things", response_model=Dict[str, Any])
def get_things(skip: int=0, limit: int=100, db: Session=Depends(get_db)):
    things = db.query(Thing).offset(skip).limit(limit).all()
    return {"@iot.count": len(things), "value": things}

@app.post("/v1.0/Things", response_model=ThingResponse)
def create_thing(thing_data: ThingCreate, db: Session=Depends(get_db)):
    existing = db.query(Thing).filter(Thing.id == thing_data.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Thing already exists")
    
    db_thing = Thing(**thing_data.dict())
    db.add(db_thing)
    db.commit()
    db.refresh(db_thing)
    return db_thing

@app.get("/v1.0/Things({thing_id})", response_model=ThingResponse)
def get_thing(thing_id: str, db: Session=Depends(get_db)):
    thing = db.query(Thing).filter(Thing.id == thing_id).first()
    if not thing:
        raise HTTPException(status_code=404, detail="Thing not found")
    return thing

@app.patch("/v1.0/Things({thing_id})", response_model=ThingResponse)
def update_thing(thing_id: str, thing_update: dict, db: Session=Depends(get_db)):
    thing = db.query(Thing).filter(Thing.id == thing_id).first()
    if not thing:
        raise HTTPException(status_code=404, detail="Thing not found")
    
    for field, value in thing_update.items():
        if hasattr(thing, field):
            setattr(thing, field, value)
    
    db.commit()
    db.refresh(thing)
    return thing

@app.delete("/v1.0/Things({thing_id})")
def delete_thing(thing_id: str, db: Session=Depends(get_db)):
    thing = db.query(Thing).filter(Thing.id == thing_id).first()
    if not thing:
        raise HTTPException(status_code=404, detail="Thing not found")
    
    db.delete(thing)
    db.commit()
    return {"message": "Thing deleted"}


## SENSORS ___________________________________________________________
@app.get("/v1.0/Sensors", response_model=Dict[str, Any])
def get_sensors(skip: int=0, limit: int=100, db: Session=Depends(get_db)):
    sensors = db.query(Sensor).offset(skip).limit(limit).all()
    return {"@iot.count": len(sensors), "value": sensors}

@app.post("/v1.0/Sensors", response_model=SensorResponse)
def create_sensor(sensor_data: SensorCreate, db: Session=Depends(get_db)):
    existing = db.query(Sensor).filter(Sensor.id == sensor_data.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Sensor already exists")
    
    db_sensor = Sensor(**sensor_data.dict())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

@app.get("/v1.0/Sensors({sensor_id})", response_model=SensorResponse)
def get_sensor(sensor_id: str, db: Session=Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor

@app.patch("/v1.0/Sensors({sensor_id})", response_model=SensorResponse)
def update_sensor(sensor_id: str, sensor_update: dict, db: Session=Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    for field, value in sensor_update.items():
        if hasattr(sensor, field):
            setattr(sensor, field, value)
    
    db.commit()
    db.refresh(sensor)
    return sensor

@app.delete("/v1.0/Sensors({sensor_id})")
def delete_sensor(sensor_id: str, db: Session=Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    db.delete(sensor)
    db.commit()
    return {"message": "Sensor deleted"}


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




## END _______________________________________________________________
# Start MQTT listener in background
threading.Thread(target=mqtt_listener.start, daemon=True).start()
