from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import engine, SessionLocal

from app.routes import thing, sensor, datastream, observation, observed_property, location, feature_of_interest

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


## ROUTES ______________

app = FastAPI(title="SensorThings API")

# Inclusion des routes
app.include_router(things.router, prefix="/Things", tags=["Things"])
app.include_router(datastreams.router, prefix="/Datastreams", tags=["Datastreams"])


## END _______________________________________________________________
# Start MQTT listener in background
threading.Thread(target=mqtt_listener.start, daemon=True).start()
