from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, BigInteger, JSON, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship
import geoalchemy2
from geoalchemy2 import Geometry

Base = declarative_base()

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
    id = Column(String, primary_key=True)
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
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    properties = Column(JSONB, default={})
    
    # Relationships
    Locations = relationship("Location",
                             secondary=thing_location,
                             back_populates="Things",
                             cascade="all, delete-orphan")
    Datastreams = relationship("Datastream",
                               back_populates="Thing")


    
## OBSERVEDPROPERTY ______________
class ObservedProperty(Base):
    __tablename__ = "observed_properties"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    definition = Column(String)
    
    # Relationships
    Datastreams = relationship("Datastream",
                               back_populates="ObservedProperty",)


## SENSOR ______________
class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text)
    encodingType = Column(String, default="application/json")
    metadata = Column(Text)
    
    # Relationships
    Datastreams = relationship("Datastream",
                               back_populates="Sensor")


## FEATURE OF INTEREST _____________
class FeatureOfInterest(Base):
    __tablename__ = "features_of_interest"
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text)
    encodingType = Column(String, default="application/geo+json")
    feature = Column(Geometry(geometry_type='POLYGON', srid=4326))
    
    # Relationships
    Observations = relationship("Observation",
                                back_populates="FeatureOfInterest")


## DATASTREAM ________________
class Datastream(Base):
    __tablename__ = "datastreams"
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text)
    observationType = Column(String, default="http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement")
    unitOfMeasurement = Column(JSONB)
    
    # Foreign keys
    thing_id = Column(String, ForeignKey("things.id"))
    sensor_id = Column(String, ForeignKey("sensors.id"))
    observed_property_id = Column(String, ForeignKey("observed_properties.id"))
    
    # Relationships
    Thing = relationship("Thing",
                         back_populates="Datastreams")
    Sensor = relationship("Sensor",
                          back_populates="Datastreams")
    ObservedProperty = relationship("ObservedProperty",
                                    back_populates="Datastreams")
    Observations = relationship("Observation",
                                back_populates="Datastream",
                                cascade="all, delete-orphan")

    
## OBSERVATION ____________
class Observation(Base):
    __tablename__ = "observations"
    id = Column(BigInteger, primary_key=True, index=True)
    
    # STA required fields
    phenomenonTime = Column(DateTime(timezone=True), nullable=False)
    result = Column(Float, nullable=False)
    resultTime = Column(DateTime(timezone=True))
    resultQuality = Column(JSONB)
    parameters = Column(JSONB)
    
    # Foreign keys
    datastream_id = Column(String, ForeignKey("datastreams.id"), nullable=False)
    feature_of_interest_id = Column(String, ForeignKey("features_of_interest.id"))
    
    # Your existing fields
    time = Column(DateTime(timezone=True), nullable=False)
    raw = Column(JSONB)
    
    # Relationships
    Datastream = relationship("Datastream",
                              back_populates="Observations")
    FeatureOfInterest = relationship("FeatureOfInterest",
                                     back_populates="Observations")
    
    # Hypertable configuration
    __table_args__ = {
        'info': {
            'timescaledb': {
                'hypertable': {
                    'time_column_name': 'phenomenonTime',
                    'chunk_time_interval': '1 day',
                    'partitioning_column': 'datastream_id',
                    'number_partitions': 4
                }
            }
        }
    }
