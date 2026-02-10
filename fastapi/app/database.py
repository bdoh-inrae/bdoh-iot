# app/database.py
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

POSTGRES_USER = os.getenv("POSTGRES_USER", "iot_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "iot_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "iot")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "timescaledb")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
for i in range(10):
    try:
        with engine.connect() as conn:
            print("DB ready!")
            break
    except OperationalError:
        print("Waiting for DB...")
        time.sleep(2)
else:
    raise RuntimeError("DB not ready after 10 retries")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
