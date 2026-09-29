"""
JAL TARANGA — PostgreSQL + PostGIS Data Access Layer
Handles live spatial queries, district analytics, watershed catchments,
and crowd-sourced incident dispatching directly from PostgreSQL.
"""

import json
import logging
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings

logger = logging.getLogger("vellam.database")


def get_db_connection():
    """Returns a new psycopg2 connection using DATABASE_URL."""
    return psycopg2.connect(settings.DATABASE_URL, connect_timeout=3)


def is_db_available() -> bool:
    """Fast check if the PostgreSQL server is reachable."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.warning(f"Database connection unavailable: {e}")
        return False


_MIGRATION_RAN = False

def ensure_schema_upgrades():
    """Applies schema migrations for columns and tables if not already present."""
    global _MIGRATION_RAN
    if _MIGRATION_RAN:
        return
    if not is_db_available():
        return
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                ALTER TABLE citizen_reports ADD COLUMN IF NOT EXISTS location_name VARCHAR(255);
                ALTER TABLE citizen_reports ADD COLUMN IF NOT EXISTS reporter_role VARCHAR(50) DEFAULT 'citizen';
                ALTER TABLE citizen_reports ADD COLUMN IF NOT EXISTS reporter_id VARCHAR(50);
                ALTER TABLE citizen_reports ADD COLUMN IF NOT EXISTS reporter_name VARCHAR(150);
                ALTER TABLE citizen_reports ADD COLUMN IF NOT EXISTS upvotes INT DEFAULT 0;
                ALTER TABLE citizen_reports ADD COLUMN IF NOT EXISTS remarks TEXT;
                ALTER TABLE citizen_reports ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(150);
                ALTER TABLE citizen_reports ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

                CREATE TABLE IF NOT EXISTS complaint_upvotes (
                    id SERIAL PRIMARY KEY,
                    report_id VARCHAR(50) NOT NULL REFERENCES citizen_reports(id) ON DELETE CASCADE,
                    user_id VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (report_id, user_id)
                );
                CREATE INDEX IF NOT EXISTS idx_upvotes_report ON complaint_upvotes(report_id);
                CREATE INDEX IF NOT EXISTS idx_upvotes_user ON complaint_upvotes(user_id);

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

                CREATE TABLE IF NOT EXISTS user_sessions (
                    token VARCHAR(128) PRIMARY KEY,
                    user_id VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);

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
            """)
            conn.commit()
        conn.close()
        _MIGRATION_RAN = True
        logger.info("Database schema upgrades verified and applied successfully.")
    except Exception as e:
        logger.warning(f"Error applying database schema upgrades: {e}")


def get_database_status() -> Dict[str, Any]:
    """Returns detailed status of PostgreSQL and PostGIS."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        pg_ver = cur.fetchone()[0]
        cur.execute("SELECT PostGIS_Version();")
        postgis_ver = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM districts;")
        d_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM river_basins;")
        b_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM citizen_reports;")
        r_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {
            "connected": True,
            "database": "vellam_db",
            "engine": "PostgreSQL + PostGIS",
            "postgis_version": postgis_ver,
            "postgresql_version": pg_ver.split(",")[0],
            "records": {
                "districts": d_count,
                "river_basins": b_count,
                "citizen_reports": r_count,
            }
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }


def get_districts_from_db() -> Optional[List[Dict[str, Any]]]:
    """Retrieves all 14 Kerala districts from PostgreSQL."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                id, name, malayalam_name as malayalam,
                vulnerability_score as vulnerability,
                total_villages as "totalVillages",
                flood_prone_villages as "floodVillages",
                landslide_prone_villages as "landslideVillages",
                mean_slope_deg as "slopeDeg",
                drainage_density as "drainageDensity",
                major_rivers as rivers_text,
                priority,
                center_lat, center_lng
            FROM districts
            ORDER BY id ASC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        if not rows:
            return None
        
        result = []
        for r in rows:
            rivers_list = [rv.strip() for rv in r["rivers_text"].split(",") if rv.strip()] if r.get("rivers_text") else []
            result.append({
                "id": r["id"],
                "name": r["name"],
                "malayalam": r["malayalam"],
                "center": [float(r["center_lat"]), float(r["center_lng"])],
                "vulnerability": r["vulnerability"],
                "drainageDensity": float(r["drainageDensity"]) if r.get("drainageDensity") else 0.0,
                "slopeDeg": float(r["slopeDeg"]) if r.get("slopeDeg") else 0.0,
                "floodRisk": "High" if r["vulnerability"] >= 80 else ("Moderate" if r["vulnerability"] >= 60 else "Low"),
                "landslideRisk": "High" if r.get("landslideVillages", 0) > 15 else "Moderate",
                "floodVillages": r["floodVillages"],
                "landslideVillages": r["landslideVillages"],
                "totalVillages": r["totalVillages"],
                "priority": r["priority"],
                "rivers": rivers_list,
                "source": "KSDMA & GSI Verified PostGIS Dataset"
            })
        return result
    except Exception as e:
        logger.warning(f"Error querying districts from DB: {e}")
        return None


def get_river_basins_from_db() -> Optional[List[Dict[str, Any]]]:
    """Retrieves river basins and their GeoJSON geometry from PostGIS."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                basin_id as id,
                name,
                malayalam_name as malayalam,
                area_sqkm as "areaSqKm",
                drainage_density,
                critical_bottleneck as bottleneck,
                mean_discharge_m3s as "meanDischargeMCM",
                ST_AsGeoJSON(geom) as geojson_str
            FROM river_basins
            ORDER BY id ASC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        if not rows:
            return None
        
        basins = []
        for r in rows:
            coords = []
            if r.get("geojson_str"):
                try:
                    geo = json.loads(r["geojson_str"])
                    if geo.get("type") == "Polygon" and geo.get("coordinates"):
                        # Leaflet uses [lat, lng]
                        coords = [[c[1], c[0]] for c in geo["coordinates"][0]]
                except Exception:
                    coords = []
            
            basins.append({
                "id": r["id"],
                "name": r["name"],
                "malayalam": r["malayalam"],
                "areaSqKm": float(r["areaSqKm"]) if r.get("areaSqKm") else 0.0,
                "drainageDensity": f"{r['drainage_density']} km/km²",
                "meanDischargeMCM": float(r["meanDischargeMCM"]) if r.get("meanDischargeMCM") else 0.0,
                "coordinates": coords,
                "bottleneck": r["bottleneck"],
                "status": "Monitored Active Basin",
            })
        return basins
    except Exception as e:
        logger.warning(f"Error querying river_basins from DB: {e}")
        return None


def get_citizen_reports_from_db(
    user_id: Optional[str] = None,
    reporter_role: Optional[str] = None,
    user_ids: Optional[List[str]] = None,
    emails: Optional[List[str]] = None,
    report_ids: Optional[List[str]] = None,
) -> Optional[List[Dict[str, Any]]]:
    """Retrieves incident reports from PostgreSQL with full metadata, location name, and upvotes."""
    ensure_schema_upgrades()
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT 
                cr.id, cr.district, cr.category, cr.severity,
                cr.description as "desc",
                cr.reporter_email as email,
                cr.photo_data as image,
                cr.status,
                cr.latitude as lat,
                cr.longitude as lng,
                COALESCE(cr.location_name, '') as location_name,
                COALESCE(cr.reporter_role, 'citizen') as reporter_role,
                COALESCE(cr.reporter_id, '') as reporter_id,
                COALESCE(cr.reporter_name, '') as reporter_name,
                COALESCE(o.designation, '') as reporter_designation,
                COALESCE(cr.upvotes, 0) as upvotes,
                COALESCE(cr.remarks, '') as remarks,
                COALESCE(cr.assigned_to, '') as assigned_to,
                TO_CHAR(cr.reported_at, 'YYYY-MM-DD HH24:MI') as "timestamp",
                TO_CHAR(COALESCE(cr.updated_at, cr.reported_at), 'YYYY-MM-DD HH24:MI') as "updated_at"
            FROM citizen_reports cr
            LEFT JOIN officers o ON (cr.reporter_id = o.id OR LOWER(cr.reporter_email) = LOWER(o.email) OR LOWER(cr.reporter_name) = LOWER(o.full_name) OR (o.username != '' AND POSITION(LOWER(o.username) IN LOWER(cr.reporter_name)) > 0))
        """
        clauses = []
        params = []

        or_clauses = []
        if user_id:
            or_clauses.append("(cr.reporter_id = %s OR LOWER(cr.reporter_email) = LOWER(%s))")
            params.extend([user_id, user_id])

        if user_ids and len(user_ids) > 0:
            clean_uids = [u.strip() for u in user_ids if u and u.strip()]
            if clean_uids:
                or_clauses.append("cr.reporter_id = ANY(%s)")
                params.append(clean_uids)

        if emails and len(emails) > 0:
            clean_emails = [e.strip().lower() for e in emails if e and e.strip()]
            if clean_emails:
                or_clauses.append("LOWER(cr.reporter_email) = ANY(%s)")
                params.append(clean_emails)

        if report_ids and len(report_ids) > 0:
            clean_rids = [r.strip() for r in report_ids if r and r.strip()]
            if clean_rids:
                or_clauses.append("cr.id = ANY(%s)")
                params.append(clean_rids)

        if or_clauses:
            clauses.append("(" + " OR ".join(or_clauses) + ")")

        if reporter_role:
            clauses.append("cr.reporter_role = %s")
            params.append(reporter_role)

        if clauses:
            query += " WHERE " + " AND ".join(clauses)

        query += " ORDER BY cr.reported_at DESC;"

        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        result = []
        for r in rows:
            d = dict(r)
            d["lat"] = float(d["lat"])
            d["lng"] = float(d["lng"])
            d["upvotes"] = int(d.get("upvotes") or 0)
            result.append(d)
        return result
    except Exception as e:
        logger.warning(f"Error querying citizen_reports from DB: {e}")
        return None


def save_session_to_db(token: str, user_id: str) -> bool:
    """Stores session token into PostgreSQL user_sessions."""
    ensure_schema_upgrades()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_sessions (token, user_id)
            VALUES (%s, %s)
            ON CONFLICT (token) DO UPDATE SET user_id = EXCLUDED.user_id;
        """, (token, user_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.warning(f"Error saving session to DB: {e}")
        return False


def get_user_id_by_session_db(token: str) -> Optional[str]:
    """Retrieves user_id by active session token from PostgreSQL."""
    ensure_schema_upgrades()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_sessions WHERE token = %s;", (token,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        logger.warning(f"Error fetching session from DB: {e}")
        return None


def delete_session_from_db(token: str) -> bool:
    """Removes a session token from PostgreSQL on logout."""
    ensure_schema_upgrades()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM user_sessions WHERE token = %s;", (token,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.warning(f"Error deleting session from DB: {e}")
        return False


def add_citizen_report_to_db(r: Any) -> Optional[Dict[str, Any]]:
    """Inserts a new geotagged field report into PostgreSQL with location details and audit trail."""
    ensure_schema_upgrades()
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT count(*) FROM citizen_reports;")
        count = cur.fetchone()["count"]
        report_id = f"UY-REP-{count + 501}"

        email = r.email.strip() if hasattr(r, "email") and r.email else ""
        image = getattr(r, "image", None)
        location_name = getattr(r, "location_name", None) or f"{r.district}, India"
        reporter_role = getattr(r, "reporter_role", "citizen") or "citizen"
        reporter_id = getattr(r, "reporter_id", "") or ""
        reporter_name = getattr(r, "reporter_name", "") or (email.split("@")[0] if email else "Citizen Reporter")
        initial_status = "Submitted"

        cur.execute("""
            INSERT INTO citizen_reports (
                id, district, category, severity, description,
                reporter_email, photo_data, status,
                latitude, longitude, location_name,
                reporter_role, reporter_id, reporter_name, upvotes,
                geom
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, 0,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            ) RETURNING id, TO_CHAR(reported_at, 'YYYY-MM-DD HH24:MI') as "timestamp";
        """, (
            report_id, r.district, r.category, r.severity, r.desc,
            email, image, initial_status,
            r.lat, r.lng, location_name,
            reporter_role, reporter_id, reporter_name,
            r.lng, r.lat
        ))
        row = cur.fetchone()

        # Insert initial timeline update
        cur.execute("""
            INSERT INTO complaint_updates (
                report_id, status, remarks, updated_by, updated_by_role
            ) VALUES (%s, %s, %s, %s, %s);
        """, (
            report_id, initial_status, "Incident logged into spatial triage queue",
            reporter_name, reporter_role
        ))

        # Create notifications
        if reporter_id:
            cur.execute("""
                INSERT INTO notifications (user_id, title, message, type, link_tab, report_id)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                reporter_id,
                f"Complaint #{report_id} Submitted",
                f"Your field report in {r.district} ({r.category}) was received and logged into the spatial queue.",
                "success", "community", report_id
            ))

        # Admin broadcast notification
        cur.execute("""
            INSERT INTO notifications (user_id, title, message, type, link_tab, report_id)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (
            "all_admins",
            f"New {reporter_role.title()} Incident #{report_id}",
            f"{reporter_name} reported {r.category} ({r.severity}) at {location_name}.",
            "alert" if r.severity in ["Critical", "High"] else "info", "admin", report_id
        ))

        conn.commit()
        cur.close()
        conn.close()

        return {
            "id": report_id,
            "district": r.district,
            "category": r.category,
            "severity": r.severity,
            "email": email,
            "timestamp": row["timestamp"],
            "lat": r.lat,
            "lng": r.lng,
            "desc": r.desc,
            "image": image,
            "location_name": location_name,
            "reporter_role": reporter_role,
            "reporter_id": reporter_id,
            "reporter_name": reporter_name,
            "upvotes": 0,
            "status": initial_status,
        }
    except Exception as e:
        logger.warning(f"Error inserting citizen report into DB: {e}")
        return None


def update_citizen_report_status_in_db(
    report_id: str,
    new_status: str,
    remarks: Optional[str] = None,
    assigned_to: Optional[str] = None,
    updated_by: Optional[str] = None,
    updated_by_role: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Updates operational status, remarks, and logs audit timeline for a report."""
    ensure_schema_upgrades()
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            UPDATE citizen_reports
            SET status = %s,
                remarks = COALESCE(%s, remarks),
                assigned_to = COALESCE(%s, assigned_to),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, district, category, reporter_id, reporter_email, status, remarks, assigned_to;
        """, (new_status, remarks, assigned_to, report_id))
        row = cur.fetchone()

        if not row:
            conn.close()
            return None

        # Insert into complaint_updates timeline
        actor_name = updated_by or "Disaster Response Authority"
        actor_role = updated_by_role or "admin"
        cur.execute("""
            INSERT INTO complaint_updates (
                report_id, status, remarks, assigned_to, updated_by, updated_by_role
            ) VALUES (%s, %s, %s, %s, %s, %s);
        """, (report_id, new_status, remarks, assigned_to, actor_name, actor_role))

        # Notify submitter
        target_user = row["reporter_id"] or row["reporter_email"]
        if target_user:
            cur.execute("""
                INSERT INTO notifications (user_id, title, message, type, link_tab, report_id)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                target_user,
                f"Complaint #{report_id} Status: {new_status}",
                f"Status updated to '{new_status}'. " + (f"Remarks: {remarks}" if remarks else ""),
                "success" if new_status == "Resolved" else ("warning" if new_status == "Rejected" else "info"),
                "community", report_id
            ))

        conn.commit()
        cur.close()
        conn.close()
        return dict(row)
    except Exception as e:
        logger.warning(f"Error updating report status in DB: {e}")
        return None


def toggle_complaint_upvote_in_db(report_id: str, user_id: str) -> Dict[str, Any]:
    """Toggles citizen upvote on a complaint, strictly enforcing 1 vote per user."""
    ensure_schema_upgrades()
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check if already voted
        cur.execute("SELECT id FROM complaint_upvotes WHERE report_id = %s AND user_id = %s;", (report_id, user_id))
        existing = cur.fetchone()

        if existing:
            # Remove upvote
            cur.execute("DELETE FROM complaint_upvotes WHERE report_id = %s AND user_id = %s;", (report_id, user_id))
            cur.execute("UPDATE citizen_reports SET upvotes = GREATEST(0, COALESCE(upvotes, 1) - 1) WHERE id = %s RETURNING upvotes;", (report_id,))
            new_count = cur.fetchone()["upvotes"]
            conn.commit()
            cur.close()
            conn.close()
            return {"success": True, "upvoted": False, "count": new_count, "upvotes": new_count, "message": "Upvote removed"}
        else:
            # Add upvote
            cur.execute("INSERT INTO complaint_upvotes (report_id, user_id) VALUES (%s, %s);", (report_id, user_id))
            cur.execute("UPDATE citizen_reports SET upvotes = COALESCE(upvotes, 0) + 1 WHERE id = %s RETURNING upvotes;", (report_id,))
            new_count = cur.fetchone()["upvotes"]
            conn.commit()
            cur.close()
            conn.close()
            return {"success": True, "upvoted": True, "count": new_count, "upvotes": new_count, "message": "Complaint upvoted"}
    except Exception as e:
        logger.warning(f"Error toggling upvote in DB: {e}")
        return {"success": False, "error": str(e)}


def get_user_upvoted_reports_from_db(user_id: str) -> List[str]:
    """Returns set of report IDs upvoted by this citizen."""
    ensure_schema_upgrades()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT report_id FROM complaint_upvotes WHERE user_id = %s;", (user_id,))
        rows = [r[0] for r in cur.fetchall()]
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        logger.warning(f"Error querying user upvotes: {e}")
        return []


def get_complaint_timeline_from_db(report_id: str) -> List[Dict[str, Any]]:
    """Returns lifecycle audit timeline for a given report ID."""
    ensure_schema_upgrades()
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                id, report_id, status, remarks, assigned_to,
                updated_by, updated_by_role,
                TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI') as timestamp
            FROM complaint_updates
            WHERE report_id = %s
            ORDER BY created_at ASC;
        """, (report_id,))
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        logger.warning(f"Error querying timeline: {e}")
        return []


def create_notification_in_db(
    user_id: str,
    title: str,
    message: str,
    n_type: str = "info",
    link_tab: str = "community",
    report_id: Optional[str] = None
) -> bool:
    """Creates a persistent notification record."""
    ensure_schema_upgrades()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notifications (user_id, title, message, type, link_tab, report_id)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (user_id, title, message, n_type, link_tab, report_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.warning(f"Error creating notification: {e}")
        return False


def get_user_notifications_from_db(user_id: str, is_admin: bool = False) -> Dict[str, Any]:
    """Retrieves notifications for user including unread counter."""
    ensure_schema_upgrades()
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if is_admin:
            cur.execute("""
                SELECT 
                    id, user_id, title, message, type, link_tab, report_id, is_read,
                    TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI') as timestamp
                FROM notifications
                WHERE user_id = %s OR user_id = 'all_admins' OR user_id = 'broadcast'
                ORDER BY created_at DESC
                LIMIT 50;
            """, (user_id,))
        else:
            cur.execute("""
                SELECT 
                    id, user_id, title, message, type, link_tab, report_id, is_read,
                    TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI') as timestamp
                FROM notifications
                WHERE user_id = %s OR user_id = 'broadcast'
                ORDER BY created_at DESC
                LIMIT 50;
            """, (user_id,))

        items = [dict(r) for r in cur.fetchall()]
        unread_count = sum(1 for n in items if not n.get("is_read"))

        cur.close()
        conn.close()
        return {"unread_count": unread_count, "notifications": items}
    except Exception as e:
        logger.warning(f"Error querying notifications: {e}")
        return {"unread_count": 0, "notifications": []}


def mark_notification_read_in_db(notif_id: Optional[int], user_id: str) -> bool:
    """Marks one or all notifications as read."""
    ensure_schema_upgrades()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if notif_id:
            cur.execute("UPDATE notifications SET is_read = TRUE WHERE id = %s;", (notif_id,))
        else:
            cur.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s OR user_id = 'all_admins';", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.warning(f"Error marking notification read: {e}")
        return False


def delete_citizen_report_from_db(report_id: str) -> bool:
    """Deletes a citizen incident report from PostgreSQL."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM citizen_reports WHERE id = %s;", (report_id,))
        deleted = cur.rowcount > 0
        conn.commit()
        cur.close()
        conn.close()
        return deleted
    except Exception as e:
        logger.warning(f"Error deleting report from DB: {e}")
        return False
