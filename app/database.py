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

def synchronization(bulk=False):
    import requests
    import zipfile
    import io
    import csv
    import os
    from app.models import agency, calendar_date, feed_info, route, shape, stop_time, stop, transfer, trip
    from sqlalchemy.orm import Session

    gtfs_urls = [
        "https://mkuran.pl/gtfs/polregio.zip",
        "https://kolejemalopolskie.com.pl/rozklady_jazdy/kml-ska-gtfs.zip",
    ]
    bulk = False
    # bulk = True
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
    print("[SYNC] Start synchronizacji GTFS")
    for url in gtfs_urls:
        print(f"[SYNC] Pobieram: {url}")
        r = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
    for file_name in z.namelist():
            print(f"[SYNC] Przetwarzam plik: {file_name}")
            if file_name in file_model_map:
                print(f"[SYNC] Importuję: {file_name}")
                with z.open(file_name) as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
                    model = file_model_map[file_name]
                    pk = list(model.__table__.primary_key.columns)[0].name
                    print(f"[SYNC] Klucz główny: {pk}")
                    if pk not in reader.fieldnames:
                        print(f"[WARN] Plik {file_name} nie zawiera kolumny klucza głównego '{pk}'. Pomijam import.")
                        continue
                    row_count = 0
                    bulk_objects = []
                    is_table_empty = db.query(model).first() is None
                    for row in reader:
                        # Zamiana pustych stringów na None dla pól typu integer
                        for col in model.__table__.columns:
                            if col.type.python_type == int:
                                if col.name in row and row[col.name] == "":
                                    row[col.name] = None
                        # Zamiana każdej godziny >= 24 na 00 w arrival_time i departure_time
                        for time_col in ["arrival_time", "departure_time"]:
                            if time_col in row and isinstance(row[time_col], str):
                                parts = row[time_col].split(":")
                                if len(parts) == 3 and parts[0].isdigit() and int(parts[0]) >= 24:
                                    row[time_col] = "00:" + parts[1] + ":" + parts[2]
                        pk_value = row[pk]
                        # Filtrowanie pól do tych, które są w modelu
                        model_columns = set(c.name for c in model.__table__.columns)
                        filtered_row = {k: v for k, v in row.items() if k in model_columns}
                        bulk_objects.append(model(**filtered_row))
                        row_count += 1
                    if bulk or is_table_empty:
                        if bulk_objects:
                            db.bulk_save_objects(bulk_objects)
                    else:
                        for obj in bulk_objects:
                            pk_value = getattr(obj, pk)
                            existing = db.query(model).filter(getattr(model, pk) == pk_value).first()
                            if existing:
                                db.query(model).filter(getattr(model, pk) == pk_value).update(obj.__dict__)
                            else:
                                db.add(obj)
                    print(f"[SYNC] Zaimportowano {row_count} rekordów z pliku {file_name}")
            else:
                print(f"[SYNC] Pomijam plik: {file_name} (brak modelu)")
    db.commit()
    print(f"[SYNC] Zatwierdzono zmiany dla {url}")
    db.close()
    print("[SYNC] Synchronizacja zakończona")
