from app.database import Base, engine
from app.models import place

Base.metadata.create_all(bind=engine)
