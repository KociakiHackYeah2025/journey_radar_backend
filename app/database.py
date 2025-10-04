from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# URL do bazy z pliku .env
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Tworzymy silnik (engine)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Sesja — czyli połączenie z bazą w ramach zapytań
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Bazowa klasa modeli
Base = declarative_base()

# Dependency do FastAPI (dla endpointów)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
