-- ==============================================================================
-- VELLAM | വെള്ളം — Kerala Geospatial Watershed Intelligence Platform
-- Master PostgreSQL + PostGIS Database Schema
-- EPSG:4326 (WGS 84) Coordinate Reference System
-- ==============================================================================

-- 1. Enable PostGIS Spatial Engine
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. Kerala Administrative Districts Table
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
    center_lat NUMERIC(9, 6),
    center_lng NUMERIC(9, 6),
    geom GEOMETRY(Geometry, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_districts_geom ON districts USING GIST (geom);

-- 3. Delineated River Basins (44 Kerala Catchments)
CREATE TABLE IF NOT EXISTS river_basins (
    id SERIAL PRIMARY KEY,
    basin_id VARCHAR(50) UNIQUE,
    name VARCHAR(150) NOT NULL,
    malayalam_name VARCHAR(150),
    area_sqkm NUMERIC(10, 2),
    drainage_density NUMERIC(5, 2),
    critical_bottleneck TEXT,
    mean_discharge_m3s NUMERIC(10, 2),
    geom GEOMETRY(Polygon, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_basins_geom ON river_basins USING GIST (geom);

-- 4. River Drainage Network (MERIT-Basins Strahler Reaches)
CREATE TABLE IF NOT EXISTS river_reaches (
    comid BIGINT PRIMARY KEY,
    basin_name VARCHAR(150),
    strahler_order INT NOT NULL,
    length_km NUMERIC(8, 2),
    upstream_area_km2 NUMERIC(10, 2),
    next_down_id BIGINT,
    geom GEOMETRY(LineString, 4326) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_reaches_geom ON river_reaches USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_reaches_sorder ON river_reaches (strahler_order);

-- 5. Citizen Field Incident & Disaster Reports
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
    geom GEOMETRY(Point, 4326),
    reported_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_reports_geom ON citizen_reports USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_reports_status ON citizen_reports (status);

-- 6. Delineated Catchments Spatial Cache
CREATE TABLE IF NOT EXISTS delineated_cache (
    id SERIAL PRIMARY KEY,
    outlet_lat NUMERIC(9, 6) NOT NULL,
    outlet_lng NUMERIC(9, 6) NOT NULL,
    area_km2 NUMERIC(10, 2) NOT NULL,
    area_ha NUMERIC(12, 2),
    reach_count INT DEFAULT 0,
    snap_distance_m NUMERIC(8, 2),
    basin_name VARCHAR(150),
    outlet_geom GEOMETRY(Point, 4326) NOT NULL,
    catchment_geom GEOMETRY(Geometry, 4326) NOT NULL,
    cached_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_cache_catchment ON delineated_cache USING GIST (catchment_geom);
CREATE INDEX IF NOT EXISTS idx_cache_outlet ON delineated_cache USING GIST (outlet_geom);

-- 7. Dedicated Officers Database Store (KSDMA Analysts, Hydrologists, Field Responders)
CREATE TABLE IF NOT EXISTS officers (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'officer',
    designation VARCHAR(150),
    department VARCHAR(200),
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_officers_username ON officers (username);

-- 8. Dedicated Citizens Database Store (Community Observers, Public Hazard Reporters)
CREATE TABLE IF NOT EXISTS citizens (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(30),
    district VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'citizen',
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_citizens_username ON citizens (username);
CREATE INDEX IF NOT EXISTS idx_citizens_district ON citizens (district);

-- 9. Dedicated Administrators Database Store (State Emergency Operations Center - SEOC)
CREATE TABLE IF NOT EXISTS administrators (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    department VARCHAR(200) DEFAULT 'State Emergency Operations Centre (SEOC)',
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Community Complaint Upvotes (1 Upvote per Citizen, Duplicate Prevention)
CREATE TABLE IF NOT EXISTS complaint_upvotes (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(50) NOT NULL REFERENCES citizen_reports(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (report_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_upvotes_report ON complaint_upvotes(report_id);
CREATE INDEX IF NOT EXISTS idx_upvotes_user ON complaint_upvotes(user_id);

-- 11. Complaint Timeline & Operational Audit Trail
CREATE TABLE IF NOT EXISTS complaint_updates (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(50) NOT NULL REFERENCES citizen_reports(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    remarks TEXT,
    assigned_to VARCHAR(150),
    updated_by VARCHAR(150),
    updated_by_role VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_updates_report ON complaint_updates(report_id);

-- 12. Persistent Notification Queue (Citizen & Admin Alerts)
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    link_tab VARCHAR(50) DEFAULT 'community',
    report_id VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);

-- 13. Persistent User Sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    token VARCHAR(128) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);

-- 14. Secure Password Recovery & Reset Tokens
CREATE TABLE IF NOT EXISTS password_resets (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    token VARCHAR(128) NOT NULL,
    role VARCHAR(50) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_pw_reset_token ON password_resets(token);
CREATE INDEX IF NOT EXISTS idx_pw_reset_user ON password_resets(user_id);



