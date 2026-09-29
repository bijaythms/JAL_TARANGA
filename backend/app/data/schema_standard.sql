-- ==============================================================================
-- VELLAM | വെള്ളം — Kerala Geospatial Watershed Intelligence Platform
-- Master Standard PostgreSQL Schema (Zero Extensions Required)
-- Works on ANY PostgreSQL installation out of the box!
-- ==============================================================================

-- 1. Kerala Administrative Districts Table
CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    malayalam_name VARCHAR(100),
    vulnerability_score INT CHECK (vulnerability_score BETWEEN 0 AND 100),
    total_villages INT DEFAULT 0,
    flood_prone_villages INT DEFAULT 0,
    landslide_prone_villages INT DEFAULT 0,
    mean_slope_deg NUMERIC(5, 2),
    drainage_density NUMERIC(5, 2),
    major_rivers TEXT,
    priority VARCHAR(50),
    center_lat NUMERIC(9, 6) NOT NULL,
    center_lng NUMERIC(9, 6) NOT NULL,
    geojson JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_districts_lat_lng ON districts (center_lat, center_lng);

-- 2. Delineated River Basins (44 Kerala Catchments)
CREATE TABLE IF NOT EXISTS river_basins (
    id SERIAL PRIMARY KEY,
    basin_id VARCHAR(50) UNIQUE,
    name VARCHAR(150) NOT NULL,
    malayalam_name VARCHAR(150),
    area_sqkm NUMERIC(10, 2),
    drainage_density NUMERIC(5, 2),
    critical_bottleneck TEXT,
    mean_discharge_m3s NUMERIC(10, 2),
    geojson JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_basins_id ON river_basins (basin_id);

-- 3. River Drainage Network (MERIT-Basins Strahler Reaches)
CREATE TABLE IF NOT EXISTS river_reaches (
    comid BIGINT PRIMARY KEY,
    basin_name VARCHAR(150),
    strahler_order INT NOT NULL,
    length_km NUMERIC(8, 2),
    upstream_area_km2 NUMERIC(10, 2),
    next_down_id BIGINT,
    geojson JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_reaches_sorder ON river_reaches (strahler_order);
CREATE INDEX IF NOT EXISTS idx_reaches_basin ON river_reaches (basin_name);

-- 4. Citizen Field Incident & Disaster Reports
CREATE TABLE IF NOT EXISTS citizen_reports (
    id VARCHAR(50) PRIMARY KEY,
    district VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    severity VARCHAR(30) NOT NULL CHECK (severity IN ('Low', 'Moderate', 'High', 'Critical')),
    description TEXT NOT NULL,
    reporter_email VARCHAR(255),
    photo_data TEXT,
    status VARCHAR(30) DEFAULT 'Pending Verification',
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    reported_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_reports_status ON citizen_reports (status);
CREATE INDEX IF NOT EXISTS idx_reports_district ON citizen_reports (district);
CREATE INDEX IF NOT EXISTS idx_reports_coords ON citizen_reports (latitude, longitude);

-- 5. Delineated Catchments Spatial Cache
CREATE TABLE IF NOT EXISTS delineated_cache (
    id SERIAL PRIMARY KEY,
    outlet_lat NUMERIC(9, 6) NOT NULL,
    outlet_lng NUMERIC(9, 6) NOT NULL,
    area_km2 NUMERIC(10, 2) NOT NULL,
    area_ha NUMERIC(12, 2),
    reach_count INT DEFAULT 0,
    snap_distance_m NUMERIC(8, 2),
    basin_name VARCHAR(150),
    geojson JSONB NOT NULL,
    cached_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_cache_outlet_coords ON delineated_cache (outlet_lat, outlet_lng);
