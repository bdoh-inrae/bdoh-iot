from fastapi import FastAPI
import threading
import logging

from database import engine, Base
from routes import (
    thing, sensor, datastream, observation,
    observed_property, location, feature_of_interest
)
import mqtt_listener


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BDOH IoT API - SensorThings Compliant")

API_PREFIX = "/v1.0"

app.include_router(thing.router, prefix=f"{API_PREFIX}/Things", tags=["Things"])
app.include_router(sensor.router, prefix=f"{API_PREFIX}/Sensors", tags=["Sensors"])
app.include_router(datastream.router, prefix=f"{API_PREFIX}/Datastreams", tags=["Datastreams"])
app.include_router(observation.router, prefix=f"{API_PREFIX}/Observations", tags=["Observations"])
app.include_router(observed_property.router, prefix=f"{API_PREFIX}/ObservedProperties", tags=["ObservedProperties"])
app.include_router(location.router, prefix=f"{API_PREFIX}/Locations", tags=["Locations"])
app.include_router(feature_of_interest.router, prefix=f"{API_PREFIX}/FeaturesOfInterest", tags=["FeaturesOfInterest"])


threading.Thread(target=mqtt_listener.start, daemon=True).start()

