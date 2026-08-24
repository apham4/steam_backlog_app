# Database operations, SessionLocal

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# SQLAlchemy engine. The core connection to PostgreSQL.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping = True, # Automatically reconnects if Neon.tech drops idle connections.
)

# sessionmaker is a class factory to dynamically generate the SessionLocal class.
# SessionLocal = session instance local to a single request/thread. Each web request receives its own isolated db session that commits or rolls back, then closes.
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)

# Same here. Declarative Base class for SQLAlchemy's declarative Object-Relational Mapping (ORM) system. Database model/table classes inherit from this.
Base = declarative_base()

# Generator function using yield used for FastAPI dependency.
def get_db():
    """Gets a database session per request and guarantees cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()