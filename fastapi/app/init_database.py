import logging
from sqlalchemy import text

from database import engine, Base
from init_database_tools import init_database_extension, init_database_optimize
import models


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Tables connues par SQLAlchemy:", Base.metadata.tables.keys())

# Extensions
init_database_extension()
logger.info("Databse extension initialised")

# Créer les tables SQLAlchemy
Base.metadata.create_all(bind=engine)
logger.info("Tables created")

# Hypertables 
init_database_optimize()
logger.info("Observations table optimized")
