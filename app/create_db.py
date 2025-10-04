from app.database import Base, engine
from app.models import *

print("Tworzenie tabel w bazie danych...")
Base.metadata.create_all(bind=engine)

print("Tabele utworzone!")
