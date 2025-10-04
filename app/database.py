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

def synchronization():
    import requests
    import zipfile
    import io
    import csv
    import os
    from app.models import agency, calendar_date, feed_info, route, shape, stop_time, stop, transfer, trip
    from sqlalchemy.orm import Session

    gtfs_urls = [
        "https://kolejemalopolskie.com.pl/rozklady_jazdy/kml-ska-gtfs.zip",
        "https://mkuran.pl/gtfs/polregio.zip"
    ]
    # Mapowanie nazw plików na modele
    file_model_map = {
        "agency.txt": agency.Agency,
        "calendar_dates.txt": calendar_date.CalendarDate,
        "feed_info.txt": feed_info.FeedInfo,
        "routes.txt": route.Route,
        "shapes.txt": shape.Shape,
        "stop_times.txt": stop_time.StopTime,
        "stops.txt": stop.Stop,
        "transfers.txt": transfer.Transfer,
        "trips.txt": trip.Trip,
    }

    db = SessionLocal()
    for url in gtfs_urls:
        print(f"Pobieram: {url}")
        r = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        for file_name in z.namelist():
            if file_name in file_model_map:
                print(f"Importuję: {file_name}")
                with z.open(file_name) as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
                    model = file_model_map[file_name]
                    pk = list(model.__table__.primary_key.columns)[0].name
                    if pk not in reader.fieldnames:
                        print(f"[WARN] Plik {file_name} nie zawiera kolumny klucza głównego '{pk}'. Pomijam import.")
                        continue
                    for row in reader:
                        # Zamiana pustych stringów na None dla pól typu integer
                        for col in model.__table__.columns:
                            if col.type.python_type == int:
                                if col.name in row and row[col.name] == "":
                                    row[col.name] = None
                        pk_value = row[pk]
                        existing = db.query(model).filter(getattr(model, pk) == pk_value).first()
                        if existing:
                            db.query(model).filter(getattr(model, pk) == pk_value).update(row)
                        else:
                            obj = model(**row)
                            db.add(obj)
        db.commit()
    db.close()
