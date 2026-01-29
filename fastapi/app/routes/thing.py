from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Thing
from app.schemas import ThingCreate, ThingResponse
from app.database import get_db

router = APIRouter()


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
