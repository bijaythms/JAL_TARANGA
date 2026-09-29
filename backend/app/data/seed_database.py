"""
JAL TARANGA — Geospatial Intelligence Engine
Automated PostgreSQL + PostGIS Database Seed Script
Populates districts, major catchments, river reaches, and sample citizen incident reports.
"""

import sys
import os
import json
import argparse
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DATA_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = DATA_DIR / "schema.sql"
DISTRICTS_FILE = DATA_DIR / "districts.json"
WATERSHEDS_FILE = DATA_DIR / "watersheds.json"


def get_connection_params():
    parser = argparse.ArgumentParser(description="Seed VELLAM PostgreSQL / PostGIS Database")
    parser.add_argument("--host", default=os.getenv("DB_HOST", "localhost"), help="Database host")
    parser.add_argument("--port", type=int, default=int(os.getenv("DB_PORT", 5432)), help="Database port")
    parser.add_argument("--user", default=os.getenv("DB_USER", "postgres"), help="Database user")
    parser.add_argument("--password", default=os.getenv("DB_PASSWORD", "postgres"), help="Database password")
    parser.add_argument("--dbname", default=os.getenv("DB_NAME", "vellam_db"), help="Target database name")
    return parser.parse_args()


def create_database_if_not_exists(host, port, user, password, dbname):
    """Connects to root 'postgres' db and creates the target database if not existing."""
    print(f"[*] Checking if database '{dbname}' exists on {host}:{port}...")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (dbname,))
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(f'CREATE DATABASE "{dbname}";')
            print(f"[+] Successfully created database: {dbname}")
        else:
            print(f"[OK] Database '{dbname}' already exists.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[!] Warning checking/creating database: {e}")
        print("    Proceeding to attempt direct connection to target db...")


def run_schema(conn):
    """Executes schema.sql containing PostGIS extension and table definitions."""
    print("[*] Executing schema.sql (Enabling PostGIS and creating spatial tables)...")
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_FILE}")
        
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()
    print("[+] Schema and PostGIS extension applied successfully.")


def seed_districts(conn):
    """Imports 14 Kerala administrative districts from districts.json."""
    if not DISTRICTS_FILE.exists():
        print(f"[!] {DISTRICTS_FILE} not found. Skipping districts seed.")
        return

    print("[*] Seeding Kerala districts...")
    with open(DISTRICTS_FILE, "r", encoding="utf-8") as f:
        districts = json.load(f)

    inserted = 0
    with conn.cursor() as cur:
        for d in districts:
            lat = d["center"][0]
            lng = d["center"][1]
            rivers_str = ", ".join(d.get("rivers", []))
            
            cur.execute("""
                INSERT INTO districts (
                    name, malayalam_name, vulnerability_score,
                    total_villages, flood_prone_villages, landslide_prone_villages,
                    mean_slope_deg, drainage_density, major_rivers, priority,
                    center_lat, center_lng, geom
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                )
                ON CONFLICT (name) DO UPDATE SET
                    malayalam_name = EXCLUDED.malayalam_name,
                    vulnerability_score = EXCLUDED.vulnerability_score,
                    flood_prone_villages = EXCLUDED.flood_prone_villages,
                    landslide_prone_villages = EXCLUDED.landslide_prone_villages,
                    mean_slope_deg = EXCLUDED.mean_slope_deg,
                    drainage_density = EXCLUDED.drainage_density,
                    major_rivers = EXCLUDED.major_rivers,
                    priority = EXCLUDED.priority,
                    center_lat = EXCLUDED.center_lat,
                    center_lng = EXCLUDED.center_lng,
                    geom = EXCLUDED.geom;
            """, (
                d["name"],
                d.get("malayalam", ""),
                d.get("vulnerability", 50),
                d.get("totalVillages", 0),
                d.get("floodVillages", 0),
                d.get("landslideVillages", 0),
                d.get("slopeDeg", 0.0),
                d.get("drainageDensity", 0.0),
                rivers_str,
                d.get("priority", "Standard"),
                lat, lng,
                lng, lat  # PostGIS ST_MakePoint takes (X, Y) -> (Longitude, Latitude)
            ))
            inserted += 1
    conn.commit()
    print(f"[+] Successfully seeded {inserted} districts.")


def seed_watersheds(conn):
    """Imports major river basins with boundary polygons from watersheds.json."""
    if not WATERSHEDS_FILE.exists():
        print(f"[!] {WATERSHEDS_FILE} not found. Skipping watersheds seed.")
        return

    print("[*] Seeding Kerala river basins & catchments...")
    with open(WATERSHEDS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        watersheds = data.get("watersheds", [])

    inserted = 0
    with conn.cursor() as cur:
        for w in watersheds:
            coords = w.get("coordinates", [])
            if not coords:
                continue

            # Ensure polygon ring is closed (first coord == last coord)
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            
            # PostGIS WKT format: POLYGON((lng lat, lng lat, ...))
            wkt_coords = ", ".join([f"{c[1]} {c[0]}" for c in coords])
            wkt_polygon = f"POLYGON(({wkt_coords}))"

            try:
                density_val = float(str(w.get("drainageDensity", "0")).split()[0])
            except Exception:
                density_val = 0.0

            cur.execute("""
                INSERT INTO river_basins (
                    basin_id, name, malayalam_name, area_sqkm,
                    drainage_density, critical_bottleneck, mean_discharge_m3s, geom
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326)
                )
                ON CONFLICT (basin_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    malayalam_name = EXCLUDED.malayalam_name,
                    area_sqkm = EXCLUDED.area_sqkm,
                    drainage_density = EXCLUDED.drainage_density,
                    critical_bottleneck = EXCLUDED.critical_bottleneck,
                    mean_discharge_m3s = EXCLUDED.mean_discharge_m3s,
                    geom = EXCLUDED.geom;
            """, (
                w["id"],
                w["name"],
                w.get("malayalam", ""),
                w.get("areaSqKm", 0.0),
                density_val,
                w.get("bottleneck", ""),
                w.get("meanDischargeMCM", 0.0),
                wkt_polygon
            ))
            inserted += 1
    conn.commit()
    print(f"[+] Successfully seeded {inserted} river basins.")


def seed_sample_reports(conn):
    """Seeds initial citizen disaster reports for the live incident feed."""
    sample_reports = [
        {
            "id": "CR-2026-001",
            "district": "Ernakulam",
            "category": "Flood Inundation",
            "severity": "Critical",
            "description": "Periyar river swelling near Aluva Shiva Temple corridor. Water level 1.2m above normal low-flow mark.",
            "reporter_email": "keralarescue@kerala.gov.in",
            "latitude": 10.1076,
            "longitude": 76.3516,
            "status": "Verified"
        },
        {
            "id": "CR-2026-002",
            "district": "Wayanad",
            "category": "Landslide / Slope Movement",
            "severity": "Critical",
            "description": "Soil slip and debris flow warning observed along Meppadi-Chooralmala tributary slope.",
            "reporter_email": "disastermgmt.wayanad@nic.in",
            "latitude": 11.5542,
            "longitude": 76.1322,
            "status": "Verified"
        },
        {
            "id": "CR-2026-003",
            "district": "Alappuzha",
            "category": "Waterlogging",
            "severity": "Moderate",
            "description": "Water logging in Kuttanad polder belt due to backwater blockage at Thottappally spillway.",
            "reporter_email": "polderwatch@alappuzha.org",
            "latitude": 9.4981,
            "longitude": 76.3388,
            "status": "Pending Verification"
        }
    ]

    with conn.cursor() as cur:
        for r in sample_reports:
            cur.execute("""
                INSERT INTO citizen_reports (
                    id, district, category, severity, description,
                    reporter_email, latitude, longitude, geom, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s
                )
                ON CONFLICT (id) DO NOTHING;
            """, (
                r["id"], r["district"], r["category"], r["severity"],
                r["description"], r["reporter_email"], r["latitude"], r["longitude"],
                r["longitude"], r["latitude"], r["status"]
            ))
    conn.commit()
    print(f"[+] Successfully seeded {len(sample_reports)} initial citizen incident reports.")


def main():
    args = get_connection_params()
    print("=" * 65)
    print("JAL TARANGA — Master PostGIS Database Initializer")
    print(f"Target: postgresql://{args.user}:****@{args.host}:{args.port}/{args.dbname}")
    print("=" * 65)

    # 1. Check or create DB
    create_database_if_not_exists(args.host, args.port, args.user, args.password, args.dbname)

    # 2. Connect to target DB
    try:
        conn = psycopg2.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            dbname=args.dbname
        )
    except psycopg2.OperationalError as e:
        print(f"\n[X] Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("  1. Is PostgreSQL server running?")
        print("  2. Did you enter the correct password for user 'postgres'?")
        print(f"  3. Run script with custom password: python seed_database.py --password YOUR_PASSWORD")
        sys.exit(1)

    try:
        # 3. Apply schema
        run_schema(conn)

        # 4. Seed tables
        seed_districts(conn)
        seed_watersheds(conn)
        seed_sample_reports(conn)

        # 5. Display summary
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM districts;")
            d_count = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM river_basins;")
            b_count = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM citizen_reports;")
            r_count = cur.fetchone()[0]

        print("\n" + "=" * 65)
        print("DATABASE INITIALIZATION COMPLETE & VERIFIED!")
        print(f"  - Districts in DB:      {d_count}")
        print(f"  - River Basins in DB:   {b_count}")
        print(f"  - Incident Reports:     {r_count}")
        print("=" * 65)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
