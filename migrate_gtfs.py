#!/usr/bin/env python3
"""
Skrypt migracyjny do ładowania danych GTFS z plików CSV do bazy danych.
"""

import csv
import os
import sys
from datetime import datetime, time, date
from pathlib import Path

# Dodaj path do katalogu app
sys.path.append(str(Path(__file__).parent))

from app.database import engine, SessionLocal, Base
from app.models.agency import Agency
from app.models.route import Route
from app.models.stop import Stop
from app.models.trip import Trip
from app.models.stop_time import StopTime
from app.models.calendar_date import CalendarDate
from app.models.shape import Shape
from app.models.transfer import Transfer
from app.models.feed_info import FeedInfo


def parse_time(time_str):
    """Parsuje czas z formatu HH:MM:SS do time object."""
    if not time_str:
        return None
    try:
        parts = time_str.split(':')
        hour = int(parts[0])
        minute = int(parts[1])
        second = int(parts[2])
        # GTFS może mieć godziny > 23 (np. 25:00 = 01:00 następnego dnia)
        if hour >= 24:
            hour = hour % 24
        return time(hour, minute, second)
    except (ValueError, IndexError):
        return None


def parse_date(date_str):
    """Parsuje datę z formatu YYYYMMDD do date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y%m%d').date()
    except ValueError:
        return None


def parse_float(value_str):
    """Parsuje float, zwraca None jeśli puste."""
    if not value_str:
        return None
    try:
        return float(value_str)
    except ValueError:
        return None


def parse_int(value_str):
    """Parsuje int, zwraca None jeśli puste."""
    if not value_str:
        return None
    try:
        return int(value_str)
    except ValueError:
        return None


def load_agencies(session, data_dir):
    """Ładuje dane z agency.txt"""
    print("Ładowanie agencies...")
    file_path = os.path.join(data_dir, 'agency.txt')
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            agency = Agency(
                agency_id=parse_int(row['agency_id']),
                agency_name=row['agency_name'],
                agency_url=row['agency_url'] or None,
                agency_timezone=row['agency_timezone'] or None,
                agency_lang=row['agency_lang'] or None,
                agency_phone=row['agency_phone'] or None,
                agency_fare_url=row['agency_fare_url'] or None,
                agency_email=row['agency_email'] or None
            )
            session.add(agency)
    
    session.commit()
    print("✓ Agencies załadowane")


def load_routes(session, data_dir):
    """Ładuje dane z routes.txt"""
    print("Ładowanie routes...")
    file_path = os.path.join(data_dir, 'routes.txt')
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            route = Route(
                route_id=row['route_id'],
                agency_id=parse_int(row['agency_id']),
                route_short_name=row['route_short_name'] or None,
                route_long_name=row['route_long_name'] or None,
                route_desc=row['route_desc'] or None,
                route_type=parse_int(row['route_type']),
                route_url=row['route_url'] or None,
                route_color=row['route_color'] or None,
                route_text_color=row['route_text_color'] or None
            )
            session.add(route)
    
    session.commit()
    print("✓ Routes załadowane")


def load_stops(session, data_dir):
    """Ładuje dane z stops.txt"""
    print("Ładowanie stops...")
    file_path = os.path.join(data_dir, 'stops.txt')
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            stop = Stop(
                stop_id=parse_int(row['stop_id']),
                stop_code=row['stop_code'] or None,
                stop_name=row['stop_name'] or None,
                stop_desc=row['stop_desc'] or None,
                stop_lat=parse_float(row['stop_lat']),
                stop_lon=parse_float(row['stop_lon']),
                stop_url=row['stop_url'] or None,
                location_type=parse_int(row['location_type']),
                parent_station=row['parent_station'] or None,
                stop_IBNR=parse_int(row['stop_IBNR'])
            )
            session.add(stop)
    
    session.commit()
    print("✓ Stops załadowane")


def load_trips(session, data_dir):
    """Ładuje dane z trips.txt"""
    print("Ładowanie trips...")
    file_path = os.path.join(data_dir, 'trips.txt')
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            trip = Trip(
                trip_id=row['trip_id'],
                route_id=row['route_id'],
                service_id=row['service_id'],
                trip_headsign=row['trip_headsign'] or None,
                trip_short_name=row['trip_short_name'] or None,
                direction_id=parse_int(row['direction_id']),
                block_id=row['block_id'] or None,
                shape_id=row['shape_id'] or None,
                wheelchair_accessible=parse_int(row['wheelchair_accessible'])
            )
            session.add(trip)
    
    session.commit()
    print("✓ Trips załadowane")


def load_stop_times(session, data_dir):
    """Ładuje dane z stop_times.txt"""
    print("Ładowanie stop_times...")
    file_path = os.path.join(data_dir, 'stop_times.txt')
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        batch_size = 1000
        batch = []
        
        for row in reader:
            stop_time = StopTime(
                trip_id=row['trip_id'],
                arrival_time=parse_time(row['arrival_time']),
                departure_time=parse_time(row['departure_time']),
                stop_id=parse_int(row['stop_id']),
                stop_sequence=parse_int(row['stop_sequence']),
                stop_headsign=row['stop_headsign'] or None,
                pickup_type=parse_int(row['pickup_type']),
                drop_off_type=parse_int(row['drop_off_type']),
                shape_dist_traveled=parse_float(row['shape_dist_traveled'])
            )
            batch.append(stop_time)
            
            if len(batch) >= batch_size:
                session.add_all(batch)
                session.commit()
                batch = []
                print(f"  Zapisano batch {len(batch)} stop_times...")
        
        # Zapisz ostatni batch
        if batch:
            session.add_all(batch)
            session.commit()
    
    print("✓ Stop_times załadowane")


def load_calendar_dates(session, data_dir):
    """Ładuje dane z calendar_dates.txt"""
    print("Ładowanie calendar_dates...")
    file_path = os.path.join(data_dir, 'calendar_dates.txt')
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        batch_size = 1000
        batch = []
        
        for row in reader:
            calendar_date = CalendarDate(
                service_id=row['service_id'],
                date=parse_date(row['date']),
                exception_type=parse_int(row['exception_type'])
            )
            batch.append(calendar_date)
            
            if len(batch) >= batch_size:
                session.add_all(batch)
                session.commit()
                batch = []
        
        # Zapisz ostatni batch
        if batch:
            session.add_all(batch)
            session.commit()
    
    print("✓ Calendar_dates załadowane")


def load_shapes(session, data_dir):
    """Ładuje dane z shapes.txt"""
    print("Ładowanie shapes...")
    file_path = os.path.join(data_dir, 'shapes.txt')
    
    # Sprawdź czy plik ma jakieś dane (shapes.txt może być pusty)
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        content = csvfile.read().strip()
        if not content or content == 'shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence,shape_dist_traveled':
            print("✓ Shapes - plik pusty, pomijam")
            return
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            shape = Shape(
                shape_id=row['shape_id'],
                shape_pt_lat=parse_float(row['shape_pt_lat']),
                shape_pt_lon=parse_float(row['shape_pt_lon']),
                shape_pt_sequence=parse_int(row['shape_pt_sequence']),
                shape_dist_traveled=parse_float(row['shape_dist_traveled'])
            )
            session.add(shape)
    
    session.commit()
    print("✓ Shapes załadowane")


def load_transfers(session, data_dir):
    """Ładuje dane z transfers.txt"""
    print("Ładowanie transfers...")
    file_path = os.path.join(data_dir, 'transfers.txt')
    
    # Sprawdź czy plik ma jakieś dane
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        content = csvfile.read().strip()
        if not content or content == 'from_stop_id,to_stop_id,transfer_type,min_transfer_time':
            print("✓ Transfers - plik pusty, pomijam")
            return
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            transfer = Transfer(
                from_stop_id=parse_int(row['from_stop_id']),
                to_stop_id=parse_int(row['to_stop_id']),
                transfer_type=parse_int(row['transfer_type']),
                min_transfer_time=parse_int(row['min_transfer_time'])
            )
            session.add(transfer)
    
    session.commit()
    print("✓ Transfers załadowane")


def load_feed_info(session, data_dir):
    """Ładuje dane z feed_info.txt"""
    print("Ładowanie feed_info...")
    file_path = os.path.join(data_dir, 'feed_info.txt')
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            feed_info = FeedInfo(
                feed_publisher_name=row['feed_publisher_name'],
                feed_publisher_url=row['feed_publisher_url'] or None,
                feed_lang=row['feed_lang'] or None,
                feed_start_date=parse_date(row['feed_start_date']),
                feed_end_date=parse_date(row['feed_end_date'])
            )
            session.add(feed_info)
    
    session.commit()
    print("✓ Feed_info załadowane")


def main():
    """Główna funkcja migracji"""
    print("=== Rozpoczynam migrację danych GTFS ===")
    
    # Ścieżka do katalogu z danymi
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    # Sprawdź czy katalog istnieje
    if not os.path.exists(data_dir):
        print(f"Błąd: Katalog {data_dir} nie istnieje!")
        sys.exit(1)
    
    # Utwórz wszystkie tabele
    print("Tworzenie tabel w bazie danych...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tabele utworzone")
    
    # Utworz sesję
    session = SessionLocal()
    
    try:
        # Wyczyść istniejące dane (opcjonalnie)
        print("Czyszczenie istniejących danych...")
        session.query(StopTime).delete()
        session.query(CalendarDate).delete()
        session.query(Trip).delete()
        session.query(Route).delete()
        session.query(Agency).delete()
        session.query(Stop).delete()
        session.query(Shape).delete()
        session.query(Transfer).delete()
        session.query(FeedInfo).delete()
        session.commit()
        print("✓ Dane wyczyszczone")
        
        # Ładuj dane w odpowiedniej kolejności (z uwagi na foreign keys)
        load_agencies(session, data_dir)
        load_routes(session, data_dir)
        load_stops(session, data_dir)
        load_trips(session, data_dir)
        load_stop_times(session, data_dir)
        load_calendar_dates(session, data_dir)
        load_shapes(session, data_dir)
        load_transfers(session, data_dir)
        load_feed_info(session, data_dir)
        
        print("\n=== Migracja zakończona pomyślnie! ===")
        
        # Statystyki
        print("\nStatystyki:")
        print(f"Agencies: {session.query(Agency).count()}")
        print(f"Routes: {session.query(Route).count()}")
        print(f"Stops: {session.query(Stop).count()}")
        print(f"Trips: {session.query(Trip).count()}")
        print(f"Stop times: {session.query(StopTime).count()}")
        print(f"Calendar dates: {session.query(CalendarDate).count()}")
        print(f"Shapes: {session.query(Shape).count()}")
        print(f"Transfers: {session.query(Transfer).count()}")
        print(f"Feed info: {session.query(FeedInfo).count()}")
        
    except Exception as e:
        print(f"Błąd podczas migracji: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()