from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, PrimaryKeyConstraint, BigInteger, JSON, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship
import geoalchemy2
from geoalchemy2 import Geometry
import uuid

from database import Base


# Association table for Thing-Location (many-to-many)
thing_location = Table(
    'thing_locations',
    Base.metadata,
    Column('thing_id', String,
           ForeignKey('things.id'),
           primary_key=True),
    Column('location_id', String,
           ForeignKey('locations.id'),
           primary_key=True)
)

## LOCATION ___________
class Location(Base):
    __tablename__ = "locations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    description = Column(Text)
    encodingType = Column(String, default="application/geo+json")
    location = Column(Geometry(geometry_type='POINT', srid=4326))
    
    # Relationships
    Things = relationship("Thing",
                          secondary=thing_location,
                          back_populates="Locations")

    
## THINGS ___________
class Thing(Base):
    __tablename__ = "things"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    properties = Column(JSONB, default={})
    
    # Relationships
    Locations = relationship("Location",
                             secondary=thing_location,
                             back_populates="Things")
    Datastreams = relationship("Datastream",
                               back_populates="Thing")


    
## OBSERVEDPROPERTY ______________
class ObservedProperty(Base):
    __tablename__ = "observed_properties"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))  
    name = Column(String, nullable=False)
    definition = Column(String)
    description = Column(Text) 
    
    Datastreams = relationship("Datastream", back_populates="ObservedProperty")

    
## SENSOR ______________
class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    encodingType = Column(String, default="application/json")
    metadata_ = Column("metadata", Text)
    
    Datastreams = relationship("Datastream", back_populates="Sensor")


## FEATURE OF INTEREST _____________
class FeatureOfInterest(Base):
    __tablename__ = "features_of_interest"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    encodingType = Column(String, default="application/geo+json")
    feature = Column(Geometry(geometry_type='GEOMETRY', srid=4326))
    
    Observations = relationship("Observation", back_populates="FeatureOfInterest")
    

## DATASTREAM ________________
class Datastream(Base):
    __tablename__ = "datastreams"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    observationType = Column(String, default="http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement")
    unitOfMeasurement = Column(JSONB)

    # manque obsrevedArea, phenomenonTime, resultTime qui est je crois une aggrégation de la période des temps des observations
    
    # Foreign keys
    thing_id = Column(String, ForeignKey("things.id"), nullable=False)
    sensor_id = Column(String, ForeignKey("sensors.id"), nullable=False)
    observed_property_id = Column(String, ForeignKey("observed_properties.id"), nullable=False)
    
    # Relationships
    Thing = relationship("Thing", back_populates="Datastreams")
    Sensor = relationship("Sensor", back_populates="Datastreams")
    ObservedProperty = relationship("ObservedProperty", back_populates="Datastreams")
    Observations = relationship("Observation",
                                back_populates="Datastream",
                                cascade="all, delete-orphan")


## OBSERVATION ____________
class Observation(Base):
    __tablename__ = "observations"
    id = Column(BigInteger, index=True, autoincrement=True)
    phenomenonTime = Column(DateTime(timezone=True), nullable=False)
    resultTime = Column(DateTime(timezone=True))
    result = Column(Float, nullable=False)
    resultQuality = Column(JSONB)
    # manque validTime
    parameters = Column(JSONB)
    
    # Foreign keys
    datastream_id = Column(String, ForeignKey("datastreams.id"), nullable=False)
    feature_of_interest_id = Column(String, ForeignKey("features_of_interest.id"))
    
    # Raw data, pas compris si on garde, est ce qu'on garde bien une obs par objet observation même si on fait des ajouts à la minute
    raw = Column(JSONB)
    
    # Relationships
    Datastream = relationship("Datastream", back_populates="Observations")
    FeatureOfInterest = relationship("FeatureOfInterest", back_populates="Observations")
    
    __table_args__ = (
        PrimaryKeyConstraint('phenomenonTime', 'datastream_id'),
    )
