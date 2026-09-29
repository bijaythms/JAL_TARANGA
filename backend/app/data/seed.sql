-- ==============================================================================
-- VELLAM | Master Data Seed Script for pgAdmin Query Tool
-- Populates 14 Kerala Districts, River Basins, and Citizen Incident Reports
-- ==============================================================================

-- 1. Insert 14 Kerala Administrative Districts
INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Thiruvananthapuram', 'തിരുവനന്തപുരം', 68, 124, 26, 8, 10.1, 2.05, 'Karamana, Neyyar, Vamanapuram', 'Medium Priority (Tier-3)', 8.5241, 76.9366, ST_SetSRID(ST_MakePoint(76.9366, 8.5241), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Kollam', 'കൊല്ലം', 63, 104, 25, 6, 7.3, 1.95, 'Kallada, Ithikkara', 'Standard Priority (Tier-4)', 8.8932, 76.6141, ST_SetSRID(ST_MakePoint(76.6141, 8.8932), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Pathanamthitta', 'പത്തനംതിട്ട', 85, 70, 42, 21, 18.4, 2.65, 'Pamba, Achankovil, Kakkad', 'High Priority (Tier-2)', 9.2648, 76.787, ST_SetSRID(ST_MakePoint(76.787, 9.2648), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Alappuzha', 'ആലപ്പുഴ', 93, 93, 72, 0, 0.4, 3.4, 'Pamba, Achankovil, Manimala', 'Critical Priority (Tier-1)', 9.4981, 76.3388, ST_SetSRID(ST_MakePoint(76.3388, 9.4981), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Kottayam', 'കോട്ടയം', 82, 95, 51, 11, 5.2, 2.45, 'Meenachil, Manimala', 'High Priority (Tier-2)', 9.5916, 76.5222, ST_SetSRID(ST_MakePoint(76.5222, 9.5916), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Idukki', 'ഇടുക്കി', 95, 65, 24, 48, 34.5, 2.92, 'Periyar, Thodupuzhayar, Muthirapuzha', 'Critical Priority (Tier-1)', 9.85, 76.9667, ST_SetSRID(ST_MakePoint(76.9667, 9.85), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Ernakulam', 'എറണാകുളം', 88, 127, 64, 3, 2.8, 2.7, 'Periyar, Muvattupuzha, Chalakudy outfall', 'High Priority (Tier-2)', 9.9816, 76.2999, ST_SetSRID(ST_MakePoint(76.2999, 9.9816), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Thrissur', 'തൃശ്ശൂർ', 79, 255, 48, 9, 6.8, 2.3, 'Chalakudy, Karuvannur, Keecheri', 'Medium Priority (Tier-3)', 10.5276, 76.2144, ST_SetSRID(ST_MakePoint(76.2144, 10.5276), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Palakkad', 'പാലക്കാട്', 64, 157, 29, 12, 8.5, 1.85, 'Bharathapuzha, Kalpathipuzha, Gayathripuzha', 'Standard Priority (Tier-4)', 10.7867, 76.6548, ST_SetSRID(ST_MakePoint(76.6548, 10.7867), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Malappuram', 'മലപ്പുറം', 75, 138, 38, 17, 13.5, 2.2, 'Bharathapuzha, Chaliyar, Kadalundi', 'Medium Priority (Tier-3)', 11.051, 76.0711, ST_SetSRID(ST_MakePoint(76.0711, 11.051), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Kozhikode', 'കോഴിക്കോട്', 72, 118, 34, 14, 11.2, 2.15, 'Chaliyar, Kallayi, Korapuzha', 'Medium Priority (Tier-3)', 11.2588, 75.7804, ST_SetSRID(ST_MakePoint(75.7804, 11.2588), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Wayanad', 'വയനാട്', 96, 49, 18, 32, 31.2, 2.85, 'Kabini, Chaliyar headwaters, Mananthavady', 'Critical Priority (Tier-1)', 11.6854, 76.132, ST_SetSRID(ST_MakePoint(76.132, 11.6854), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Kannur', 'കണ്ണൂർ', 58, 132, 21, 7, 8.0, 1.9, 'Valapattanam, Anjarakandi, Kuppam', 'Standard Priority (Tier-4)', 11.8745, 75.3704, ST_SetSRID(ST_MakePoint(75.3704, 11.8745), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

INSERT INTO districts (name, malayalam_name, vulnerability_score, total_villages, flood_prone_villages, landslide_prone_villages, mean_slope_deg, drainage_density, major_rivers, priority, center_lat, center_lng, geom)
VALUES ('Kasaragod', 'കാസർഗോഡ്', 52, 128, 19, 2, 5.4, 1.75, 'Chandragiri, Karyangod, Shiriya', 'Standard Priority (Tier-4)', 12.5102, 74.9852, ST_SetSRID(ST_MakePoint(74.9852, 12.5102), 4326))
ON CONFLICT (name) DO UPDATE SET vulnerability_score = EXCLUDED.vulnerability_score, center_lat = EXCLUDED.center_lat, center_lng = EXCLUDED.center_lng;

-- 2. Insert River Basins & Boundary Polygons
INSERT INTO river_basins (basin_id, name, malayalam_name, area_sqkm, drainage_density, critical_bottleneck, mean_discharge_m3s, geom)
VALUES ('WS-PERIYAR', 'Periyar River Basin (5398 km²)', 'പെരിയാർ നദീതടം', 5398, 2.95, 'Aluva-Kalady-Eloor industrial river corridor', 11607, ST_GeomFromText('POLYGON((76.22 10.19, 76.45 10.25, 76.8 10.12, 77.1 9.95, 77.25 9.75, 77.2 9.55, 76.85 9.6, 76.4 9.9, 76.22 10.19))', 4326))
ON CONFLICT (basin_id) DO UPDATE SET area_sqkm = EXCLUDED.area_sqkm, geom = EXCLUDED.geom;

INSERT INTO river_basins (basin_id, name, malayalam_name, area_sqkm, drainage_density, critical_bottleneck, mean_discharge_m3s, geom)
VALUES ('WS-BHARATHA', 'Bharathapuzha (Nila) Basin (6186 km²)', 'ഭാരതപ്പുഴ തടം', 6186, 2.1, 'Palakkad Gap alluvial run & Chamravattom regulator', 3979, ST_GeomFromText('POLYGON((75.92 10.82, 76.28 10.78, 76.68 10.85, 76.92 10.7, 76.7 10.5, 76.2 10.6, 75.95 10.74, 75.92 10.82))', 4326))
ON CONFLICT (basin_id) DO UPDATE SET area_sqkm = EXCLUDED.area_sqkm, geom = EXCLUDED.geom;

INSERT INTO river_basins (basin_id, name, malayalam_name, area_sqkm, drainage_density, critical_bottleneck, mean_discharge_m3s, geom)
VALUES ('WS-PAMBA', 'Pamba - Achankovil Catchment (2235 km²)', 'പമ്പ - അച്ചൻകോവിൽ തടം', 2235, 3.15, 'Upper Kuttanad delta depression (-1.5m MSL)', 4642, ST_GeomFromText('POLYGON((76.35 9.4, 76.65 9.35, 77.0 9.48, 77.22 9.38, 77.1 9.15, 76.6 9.18, 76.38 9.3, 76.35 9.4))', 4326))
ON CONFLICT (basin_id) DO UPDATE SET area_sqkm = EXCLUDED.area_sqkm, geom = EXCLUDED.geom;

INSERT INTO river_basins (basin_id, name, malayalam_name, area_sqkm, drainage_density, critical_bottleneck, mean_discharge_m3s, geom)
VALUES ('WS-CHALIYAR', 'Chaliyar River Basin (2923 km²)', 'ചാലിയാർ തടം', 2923, 2.8, 'Nilambur/Meppadi debris runoff channels', 5690, ST_GeomFromText('POLYGON((75.8 11.15, 76.15 11.3, 76.28 11.58, 76.42 11.45, 76.35 11.2, 75.98 11.08, 75.8 11.15))', 4326))
ON CONFLICT (basin_id) DO UPDATE SET area_sqkm = EXCLUDED.area_sqkm, geom = EXCLUDED.geom;

-- 3. Initial Citizen Disaster Incident Reports
INSERT INTO citizen_reports (id, district, category, severity, description, reporter_email, latitude, longitude, geom, status)
VALUES 
('CR-2026-001', 'Ernakulam', 'Flood Inundation', 'Critical', 'Periyar river swelling near Aluva Shiva Temple corridor. Water level 1.2m above normal low-flow mark.', 'keralarescue@kerala.gov.in', 10.1076, 76.3516, ST_SetSRID(ST_MakePoint(76.3516, 10.1076), 4326), 'Verified'),
('CR-2026-002', 'Wayanad', 'Landslide / Slope Movement', 'Critical', 'Soil slip and debris flow warning observed along Meppadi-Chooralmala tributary slope.', 'disastermgmt.wayanad@nic.in', 11.5542, 76.1322, ST_SetSRID(ST_MakePoint(76.1322, 11.5542), 4326), 'Verified'),
('CR-2026-003', 'Alappuzha', 'Waterlogging', 'Moderate', 'Water logging in Kuttanad polder belt due to backwater blockage at Thottappally spillway.', 'polderwatch@alappuzha.org', 9.4981, 76.3388, ST_SetSRID(ST_MakePoint(76.3388, 9.4981), 4326), 'Pending Verification')
ON CONFLICT (id) DO NOTHING;
