from app.database import Base, engine
from app.models.user import User
from app.models.place import Place  # jeśli masz też model Place

Base.metadata.create_all(bind=engine)

print("Tabele utworzone!")
