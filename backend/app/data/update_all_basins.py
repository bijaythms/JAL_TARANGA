import json
import psycopg2
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

ALL_BASINS = [
    {
        "id": "WS-PERIYAR",
        "name": "Periyar River Basin (5398 km²)",
        "malayalam": "",
        "areaSqKm": 5398,
        "lengthKm": 244,
        "drainageDensity": "2.95 km/km²",
        "meanDischargeMCM": 11607,
        "coordinates": [
            [10.19, 76.22], [10.25, 76.45], [10.12, 76.8], [9.95, 77.1],
            [9.75, 77.25], [9.55, 77.2], [9.6, 76.85], [9.9, 76.4], [10.19, 76.22]
        ],
        "bottleneck": "Aluva-Kalady-Eloor industrial river corridor",
        "status": "High Flood Exposure Zone"
    },
    {
        "id": "WS-BHARATHA",
        "name": "Bharathapuzha (Nila) Basin (6186 km²)",
        "malayalam": "",
        "areaSqKm": 6186,
        "lengthKm": 209,
        "drainageDensity": "2.10 km/km²",
        "meanDischargeMCM": 3979,
        "coordinates": [
            [10.82, 75.92], [10.78, 76.28], [10.85, 76.68], [10.7, 76.92],
            [10.5, 76.7], [10.6, 76.2], [10.74, 75.95], [10.82, 75.92]
        ],
        "bottleneck": "Palakkad Gap alluvial run & Chamravattom regulator",
        "status": "Seasonal Drought & Flash Flood Susceptibility"
    },
    {
        "id": "WS-PAMBA",
        "name": "Pamba River Basin (2235 km²)",
        "malayalam": "",
        "areaSqKm": 2235,
        "lengthKm": 176,
        "drainageDensity": "3.15 km/km²",
        "meanDischargeMCM": 4642,
        "coordinates": [
            [9.4, 76.35], [9.35, 76.65], [9.48, 77.0], [9.38, 77.22],
            [9.15, 77.1], [9.18, 76.6], [9.3, 76.38], [9.4, 76.35]
        ],
        "bottleneck": "Upper Kuttanad delta depression (-1.5m MSL)",
        "status": "Severe Inundation Hotspot"
    },
    {
        "id": "WS-CHALIYAR",
        "name": "Chaliyar River Basin (2923 km²)",
        "malayalam": "",
        "areaSqKm": 2923,
        "lengthKm": 169,
        "drainageDensity": "2.80 km/km²",
        "meanDischargeMCM": 5690,
        "coordinates": [
            [11.15, 75.8], [11.3, 76.15], [11.58, 76.28], [11.45, 76.42],
            [11.2, 76.35], [11.08, 75.98], [11.15, 75.8]
        ],
        "bottleneck": "Nilambur/Meppadi debris runoff channels",
        "status": "Severe Landslide Trigger Catchment"
    },
    {
        "id": "WS-CHALAKUDY",
        "name": "Chalakudy River Basin (1704 km²)",
        "malayalam": "",
        "areaSqKm": 1704,
        "lengthKm": 145,
        "drainageDensity": "2.84 km/km²",
        "meanDischargeMCM": 2110,
        "coordinates": [
            [10.22, 76.32], [10.5, 76.38], [10.8, 76.42], [10.95, 76.28],
            [10.75, 76.15], [10.45, 76.18], [10.22, 76.32]
        ],
        "bottleneck": "Athirappilly gorge & Mala alluvial plain",
        "status": "Flash Inundation Hazard Corridor"
    },
    {
        "id": "WS-KALLADA",
        "name": "Kallada River Basin (1699 km²)",
        "malayalam": "",
        "areaSqKm": 1699,
        "lengthKm": 121,
        "drainageDensity": "2.75 km/km²",
        "meanDischargeMCM": 2216,
        "coordinates": [
            [8.98, 76.55], [9.12, 76.78], [9.05, 77.12], [8.88, 77.18],
            [8.82, 76.85], [8.98, 76.55]
        ],
        "bottleneck": "Thenmala Dam spillway & Ashtamudi outfall",
        "status": "Reservoir Regulated Floodplain"
    },
    {
        "id": "WS-MUVATTUPUZHA",
        "name": "Muvattupuzha River Basin (1571 km²)",
        "malayalam": "",
        "areaSqKm": 1571,
        "lengthKm": 121,
        "drainageDensity": "2.90 km/km²",
        "meanDischargeMCM": 3840,
        "coordinates": [
            [9.85, 76.42], [10.02, 76.58], [9.98, 76.85], [9.78, 76.82],
            [9.75, 76.48], [9.85, 76.42]
        ],
        "bottleneck": "Muvattupuzha tri-river confluence (Kaliyar, Kothamangalam, Thodupuzha)",
        "status": "Idukki Tailrace Discharge Corridor"
    },
    {
        "id": "WS-VALAPATTANAM",
        "name": "Valapattanam River Basin (1867 km²)",
        "malayalam": "",
        "areaSqKm": 1867,
        "lengthKm": 110,
        "drainageDensity": "2.65 km/km²",
        "meanDischargeMCM": 2980,
        "coordinates": [
            [11.92, 75.35], [12.08, 75.52], [12.15, 75.82], [11.95, 75.75],
            [11.88, 75.45], [11.92, 75.35]
        ],
        "bottleneck": "Pazhassi Barrage & Azhikkal estuary",
        "status": "North Malabar Estuary Drainage"
    },
    {
        "id": "WS-ACHENKOVIL",
        "name": "Achenkovil River Basin (1484 km²)",
        "malayalam": "",
        "areaSqKm": 1484,
        "lengthKm": 128,
        "drainageDensity": "2.70 km/km²",
        "meanDischargeMCM": 2340,
        "coordinates": [
            [9.25, 76.48], [9.28, 76.75], [9.15, 77.15], [8.98, 77.05],
            [9.12, 76.62], [9.25, 76.48]
        ],
        "bottleneck": "Mavelikkara-Pandalam meander corridor",
        "status": "Upper Kuttanad Flood Feeder"
    },
    {
        "id": "WS-MEENACHIL",
        "name": "Meenachil River Basin (1272 km²)",
        "malayalam": "",
        "areaSqKm": 1272,
        "lengthKm": 78,
        "drainageDensity": "2.85 km/km²",
        "meanDischargeMCM": 1810,
        "coordinates": [
            [9.58, 76.45], [9.72, 76.65], [9.75, 76.92], [9.62, 76.85],
            [9.52, 76.52], [9.58, 76.45]
        ],
        "bottleneck": "Pala-Kottayam urban river corridor & Vembanad outfall",
        "status": "Flash Flood & Urban Inundation Zone"
    },
    {
        "id": "WS-MANIMALA",
        "name": "Manimala River Basin (847 km²)",
        "malayalam": "",
        "areaSqKm": 847,
        "lengthKm": 90,
        "drainageDensity": "2.92 km/km²",
        "meanDischargeMCM": 1420,
        "coordinates": [
            [9.42, 76.55], [9.52, 76.72], [9.58, 76.95], [9.45, 76.88],
            [9.38, 76.60], [9.42, 76.55]
        ],
        "bottleneck": "Kallooppara & Thottappally lead channel",
        "status": "High Peak Discharge Catchment"
    },
    {
        "id": "WS-KARUVANNUR",
        "name": "Karuvannur River Basin (1054 km²)",
        "malayalam": "",
        "areaSqKm": 1054,
        "lengthKm": 86,
        "drainageDensity": "2.68 km/km²",
        "meanDischargeMCM": 1540,
        "coordinates": [
            [10.35, 76.15], [10.45, 76.32], [10.52, 76.62], [10.38, 76.58],
            [10.30, 76.22], [10.35, 76.15]
        ],
        "bottleneck": "Peechi Dam & Kole wetlands overflow",
        "status": "Thrissur Kole Buffer Sub-basin"
    },
    {
        "id": "WS-KADALUNDI",
        "name": "Kadalundi River Basin (1122 km²)",
        "malayalam": "",
        "areaSqKm": 1122,
        "lengthKm": 130,
        "drainageDensity": "2.55 km/km²",
        "meanDischargeMCM": 1960,
        "coordinates": [
            [11.12, 75.82], [11.18, 76.12], [11.15, 76.38], [10.98, 76.28],
            [11.02, 75.92], [11.12, 75.82]
        ],
        "bottleneck": "Kadalundi Bird Sanctuary estuary & Hajirapally bridge",
        "status": "Estuarine Bird Haven & Floodplain"
    },
    {
        "id": "WS-KUTTIYADI",
        "name": "Kuttiyadi River Basin (583 km²)",
        "malayalam": "",
        "areaSqKm": 583,
        "lengthKm": 74,
        "drainageDensity": "2.80 km/km²",
        "meanDischargeMCM": 1120,
        "coordinates": [
            [11.55, 75.65], [11.68, 75.82], [11.65, 76.02], [11.48, 75.88],
            [11.55, 75.65]
        ],
        "bottleneck": "Kuttiyadi Dam & Peruvannamuzhi reservoir",
        "status": "Kozhikode Power & Irrigation Catchment"
    },
    {
        "id": "WS-CHANDRAGIRI",
        "name": "Chandragiri River Basin (1406 km²)",
        "malayalam": "",
        "areaSqKm": 1406,
        "lengthKm": 105,
        "drainageDensity": "2.40 km/km²",
        "meanDischargeMCM": 2420,
        "coordinates": [
            [12.48, 75.02], [12.55, 75.25], [12.45, 75.52], [12.28, 75.38],
            [12.48, 75.02]
        ],
        "bottleneck": "Kasaragod Chandragiri Fort estuary",
        "status": "Northernmost Major Western Ghats Basin"
    },
    {
        "id": "WS-KARAMANA",
        "name": "Karamana River Basin (702 km²)",
        "malayalam": "",
        "areaSqKm": 702,
        "lengthKm": 68,
        "drainageDensity": "2.60 km/km²",
        "meanDischargeMCM": 920,
        "coordinates": [
            [8.45, 76.95], [8.58, 77.05], [8.65, 77.22], [8.52, 77.18],
            [8.45, 76.95]
        ],
        "bottleneck": "Peppara Dam & Thiruvananthapuram city outfall",
        "status": "Capital Urban Water Lifeline"
    },
    {
        "id": "WS-ITHIKKARA",
        "name": "Ithikkara River Basin (660 km²)",
        "malayalam": "",
        "areaSqKm": 660,
        "lengthKm": 56,
        "drainageDensity": "2.50 km/km²",
        "meanDischargeMCM": 840,
        "coordinates": [
            [8.82, 76.68], [8.92, 76.85], [8.88, 77.08], [8.75, 76.95],
            [8.82, 76.68]
        ],
        "bottleneck": "Paravur Kayal confluence",
        "status": "Southern Wetland Catchment"
    },
    {
        "id": "WS-NEYYAR",
        "name": "Neyyar River Basin (497 km²)",
        "malayalam": "",
        "areaSqKm": 497,
        "lengthKm": 56,
        "drainageDensity": "2.70 km/km²",
        "meanDischargeMCM": 680,
        "coordinates": [
            [8.35, 77.05], [8.52, 77.15], [8.55, 77.30], [8.38, 77.22],
            [8.35, 77.05]
        ],
        "bottleneck": "Neyyar Dam & Poovar estuary",
        "status": "Southernmost River Basin"
    },
    {
        "id": "WS-VAMANAPURAM",
        "name": "Vamanapuram River Basin (687 km²)",
        "malayalam": "",
        "areaSqKm": 687,
        "lengthKm": 88,
        "drainageDensity": "2.65 km/km²",
        "meanDischargeMCM": 890,
        "coordinates": [
            [8.65, 76.82], [8.78, 76.98], [8.82, 77.18], [8.68, 77.12],
            [8.65, 76.82]
        ],
        "bottleneck": "Anchuthengu Kayal outfall",
        "status": "Attingal Watershed Zone"
    },
    {
        "id": "WS-KUPPAM",
        "name": "Kuppam River Basin (469 km²)",
        "malayalam": "",
        "areaSqKm": 469,
        "lengthKm": 82,
        "drainageDensity": "2.50 km/km²",
        "meanDischargeMCM": 760,
        "coordinates": [
            [12.02, 75.32], [12.18, 75.48], [12.25, 75.68], [12.08, 75.58],
            [12.02, 75.32]
        ],
        "bottleneck": "Pazhayangadi backwater estuary",
        "status": "Kannur Agrarian River Basin"
    },
    {
        "id": "WS-KABINI",
        "name": "Kabini East-Flowing Basin (2311 km²)",
        "malayalam": "",
        "areaSqKm": 2311,
        "lengthKm": 140,
        "drainageDensity": "2.85 km/km²",
        "meanDischargeMCM": 3200,
        "coordinates": [
            [11.62, 75.98], [11.82, 76.15], [11.95, 76.42], [11.68, 76.35],
            [11.62, 75.98]
        ],
        "bottleneck": "Banasurasagar Dam & Karapuzha spillways",
        "status": "Wayanad Plateau East-Flowing Cauvery Tributary"
    },
    {
        "id": "WS-BHAVANI",
        "name": "Bhavani East-Flowing Basin (562 km²)",
        "malayalam": "",
        "areaSqKm": 562,
        "lengthKm": 84,
        "drainageDensity": "2.60 km/km²",
        "meanDischargeMCM": 920,
        "coordinates": [
            [11.05, 76.48], [11.18, 76.62], [11.12, 76.82], [10.98, 76.72],
            [11.05, 76.48]
        ],
        "bottleneck": "Attappadi Silent Valley gorge",
        "status": "Cauvery Basin Tributary"
    },
    {
        "id": "WS-PAMBAR",
        "name": "Pambar East-Flowing Basin (384 km²)",
        "malayalam": "",
        "areaSqKm": 384,
        "lengthKm": 40,
        "drainageDensity": "2.75 km/km²",
        "meanDischargeMCM": 540,
        "coordinates": [
            [10.15, 77.12], [10.32, 77.22], [10.28, 77.38], [10.08, 77.28],
            [10.15, 77.12]
        ],
        "bottleneck": "Marayoor Sandalwood reserve gorge",
        "status": "Amaravathi & Cauvery East-Flowing Basin"
    }
]

# 1. Update watersheds.json
ws_file = DATA_DIR / "watersheds.json"
with open(ws_file, "r", encoding="utf-8") as f:
    data = json.load(f)

data["watersheds"] = ALL_BASINS

with open(ws_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"[+] Updated watersheds.json with all {len(ALL_BASINS)} Kerala River Basins!")

# 2. Insert into PostgreSQL river_basins
try:
    conn = psycopg2.connect("postgresql://postgres:bijay@localhost:5432/vellam_db")
    cur = conn.cursor()

    for w in ALL_BASINS:
        coords = list(w["coordinates"])
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        wkt_coords = ", ".join([f"{c[1]} {c[0]}" for c in coords])
        wkt = f"POLYGON(({wkt_coords}))"
        density_val = float(str(w["drainageDensity"]).split()[0])

        cur.execute("""
            INSERT INTO river_basins (basin_id, name, malayalam_name, area_sqkm, drainage_density, critical_bottleneck, mean_discharge_m3s, geom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
            ON CONFLICT (basin_id) DO UPDATE SET
                name = EXCLUDED.name,
                malayalam_name = EXCLUDED.malayalam_name,
                area_sqkm = EXCLUDED.area_sqkm,
                drainage_density = EXCLUDED.drainage_density,
                critical_bottleneck = EXCLUDED.critical_bottleneck,
                mean_discharge_m3s = EXCLUDED.mean_discharge_m3s,
                geom = EXCLUDED.geom;
        """, (
            w["id"], w["name"], w["malayalam"], w["areaSqKm"], density_val,
            w["bottleneck"], w["meanDischargeMCM"], wkt
        ))

    conn.commit()
    cur.execute("SELECT count(*) FROM river_basins;")
    total = cur.fetchone()[0]
    print(f"[+] Successfully synced {total} River Basins into PostgreSQL (vellam_db)!")
    cur.close()
    conn.close()
except Exception as e:
    print(f"[!] PostgreSQL sync error: {e}")
