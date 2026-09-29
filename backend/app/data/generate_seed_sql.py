import json
from pathlib import Path

data_dir = Path(__file__).resolve().parent
with open(data_dir / 'districts.json', encoding='utf-8') as f:
    districts = json.load(f)

with open(data_dir / 'watersheds.json', encoding='utf-8') as f:
    watersheds_data = json.load(f)
    watersheds = watersheds_data.get('watersheds', [])

lines = ['-- ==============================================================================\n']
lines.append('-- VELLAM | Master Data Seed Script for pgAdmin Query Tool\n')
lines.append('-- Populates 14 Kerala Districts, River Basins, and Citizen Incident Reports\n')
lines.append('-- ==============================================================================\n\n')

lines.append('-- 1. Insert 14 Kerala Administrative Districts\n')
for d in districts:
    lat = d['center'][0]
    lng = d['center'][1]
    name = d['name'].replace("'", "''")
    mal = d.get('malayalam', '').replace("'", "''")
    rivers = ', '.join(d.get('rivers', [])).replace("'", "''")
    priority = d.get('priority', '').replace("'", "''")
    vuln = d.get('vulnerability', 50)
    tv = d.get('totalVillages', 0)
    fv = d.get('floodVillages', 0)
    lv = d.get('landslideVillages', 0)
    slope = d.get('slopeDeg', 0.0)
    dd = d.get('drainageDensity', 0.0)
    
    sql = (
        f"INSERT INTO districts (name, malayalam_name, vulnerability_score, "
        f"total_villages, flood_prone_villages, landslide_prone_villages, "
        f"mean_slope_deg, drainage_density, major_rivers, priority, "
        f"center_lat, center_lng, geom)\n"
        f"VALUES ('{name}', '{mal}', {vuln}, {tv}, {fv}, {lv}, {slope}, {dd}, "
        f"'{rivers}', '{priority}', {lat}, {lng}, ST_SetSRID(ST_MakePoint({lng}, {lat}), 4326))\n"
        f"ON CONFLICT (name) DO UPDATE SET "
        f"vulnerability_score = EXCLUDED.vulnerability_score, "
        f"center_lat = EXCLUDED.center_lat, "
        f"center_lng = EXCLUDED.center_lng;\n\n"
    )
    lines.append(sql)

lines.append('-- 2. Insert River Basins & Boundary Polygons\n')
for w in watersheds:
    coords = w.get('coordinates', [])
    if not coords:
        continue
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    wkt_coords = ', '.join([f"{c[1]} {c[0]}" for c in coords])
    wkt = f"POLYGON(({wkt_coords}))"
    bid = w['id'].replace("'", "''")
    bname = w['name'].replace("'", "''")
    bmal = w.get('malayalam', '').replace("'", "''")
    area = w.get('areaSqKm', 0.0)
    try:
        dd = float(str(w.get('drainageDensity', '0')).split()[0])
    except Exception:
        dd = 0.0
    bottleneck = w.get('bottleneck', '').replace("'", "''")
    mean_dis = w.get('meanDischargeMCM', 0.0)
    
    sql = (
        f"INSERT INTO river_basins (basin_id, name, malayalam_name, area_sqkm, "
        f"drainage_density, critical_bottleneck, mean_discharge_m3s, geom)\n"
        f"VALUES ('{bid}', '{bname}', '{bmal}', {area}, {dd}, '{bottleneck}', {mean_dis}, "
        f"ST_GeomFromText('{wkt}', 4326))\n"
        f"ON CONFLICT (basin_id) DO UPDATE SET "
        f"area_sqkm = EXCLUDED.area_sqkm, "
        f"geom = EXCLUDED.geom;\n\n"
    )
    lines.append(sql)

lines.append('-- 3. Initial Citizen Disaster Incident Reports\n')
lines.append("""INSERT INTO citizen_reports (id, district, category, severity, description, reporter_email, latitude, longitude, geom, status)
VALUES 
('CR-2026-001', 'Ernakulam', 'Flood Inundation', 'Critical', 'Periyar river swelling near Aluva Shiva Temple corridor. Water level 1.2m above normal low-flow mark.', 'keralarescue@kerala.gov.in', 10.1076, 76.3516, ST_SetSRID(ST_MakePoint(76.3516, 10.1076), 4326), 'Verified'),
('CR-2026-002', 'Wayanad', 'Landslide / Slope Movement', 'Critical', 'Soil slip and debris flow warning observed along Meppadi-Chooralmala tributary slope.', 'disastermgmt.wayanad@nic.in', 11.5542, 76.1322, ST_SetSRID(ST_MakePoint(76.1322, 11.5542), 4326), 'Verified'),
('CR-2026-003', 'Alappuzha', 'Waterlogging', 'Moderate', 'Water logging in Kuttanad polder belt due to backwater blockage at Thottappally spillway.', 'polderwatch@alappuzha.org', 9.4981, 76.3388, ST_SetSRID(ST_MakePoint(76.3388, 9.4981), 4326), 'Pending Verification')
ON CONFLICT (id) DO NOTHING;
""")

with open(data_dir / 'seed.sql', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('SUCCESS: seed.sql generated successfully!')
