from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Sensor
from app.schemas import SensorCreate, SensorResponse
from app.database import get_db

router = APIRouter()


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
