import logging
from sqlalchemy import text
from database import engine

logger = logging.getLogger(__name__)


def init_database_extension():
    """Initialize all database extensions"""
    with engine.connect() as conn:
        try:
            logger.info("Initializing database extensions...")
            
            # Enable required extensions
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
            
            conn.commit()
            logger.info("Database extensions enabled")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            conn.rollback()
            raise

        
def init_database_optimize():
    """Convert observations to optimized TimescaleDB hypertable with YOUR requirements"""
    with engine.connect() as conn:
        try:
            # Check if already a hypertable
            is_hypertable = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM timescaledb_information.hypertables 
                    WHERE hypertable_name = 'observations'
                )
            """)).scalar()
            
            if is_hypertable:
                logger.info("Observations table is already a hypertable")
                return
            
            logger.info("Converting observations to hypertable with 1-day chunks...")
            
            # 1. Create hypertable with 1-day chunks
            conn.execute(text("""
                SELECT create_hypertable(
                    'observations', 
                    'phenomenonTime',
                    chunk_time_interval => INTERVAL '1 day',  -- Daily chunks
                    if_not_exists => TRUE
                )
            """))
            
            # 2. Add space partitioning for parallel queries
            conn.execute(text("""
                SELECT add_dimension(
                    'observations',
                    'datastream_id',
                    number_partitions => 4
                )
            """))
            
            # 3. Create optimized indexes
            conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_observations_datastream_time 
            ON observations (datastream_id, "phenomenonTime" DESC)
            """))
            
            # 4. Enable compression (but don't auto-compress yet)
            conn.execute(text("""
                ALTER TABLE observations SET (
                    timescaledb.compress,
                    timescaledb.compress_segmentby = 'datastream_id',
                    timescaledb.compress_orderby = '"phenomenonTime" DESC'
                )
            """))
            
            # 5. Add compression policy - compress chunks older than 1 YEAR
            conn.execute(text("""
                SELECT add_compression_policy(
                    'observations', 
                    INTERVAL '1 year',  -- COMPRESS AFTER 1 YEAR
                    if_not_exists => TRUE
                )
            """))
            
            # 6. NO RETENTION POLICY - KEEP ALL DATA FOREVER
            # (We don't add any retention policy)
            conn.commit()
            logger.info("""
                Observations table optimized as TimescaleDB hypertable:
                - 1-day chunks for daily queries
                - Compression after 1 year
                - NO data deletion (keeps all data forever)
            """)
            
        except Exception as e:
            logger.error(f"Failed to optimize observations table: {e}")
            conn.rollback()
            raise
