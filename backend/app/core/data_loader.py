"""
VELLAM Geospatial Platform - Scientific Data Loader
Handles loading, caching, and querying of districts, watersheds, protected landmarks,
and crowd-sourced incident reports.
"""

import json
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.database import (
    get_districts_from_db,
    get_river_basins_from_db,
    get_citizen_reports_from_db,
    add_citizen_report_to_db,
    update_citizen_report_status_in_db,
    delete_citizen_report_from_db,
    toggle_complaint_upvote_in_db,
    get_user_upvoted_reports_from_db,
    get_complaint_timeline_from_db,
    create_notification_in_db,
    get_user_notifications_from_db,
    mark_notification_read_in_db,
)

_lock = threading.Lock()

# Sample Proof Images for Pre-seeded Reports
SAMPLE_LANDSLIDE_IMG = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 350'>"
    "<rect width='600' height='350' fill='%23081515'/>"
    "<path d='M0,280 L180,140 L320,220 L480,90 L600,260 L600,350 L0,350 Z' fill='%231b3233'/>"
    "<path d='M140,160 L240,290 L290,260 L380,330 L110,340 Z' fill='%23b91c1c' opacity='0.75'/>"
    "<text x='30' y='50' fill='%23ef4444' font-family='sans-serif' font-weight='bold' font-size='18'>"
    "⚠️ JAL TARANGA GEOTAG PROOF: SLOPE TENSION CRACK [WAYANAD]"
    "</text>"
    "<text x='30' y='75' fill='%2300E5FF' font-family='monospace' font-size='13'>"
    "COORDINATES: 11.5300 N, 76.1800 E • KSDMA GEOMORPHIC MONITORING"
    "</text>"
    "</svg>"
)

SAMPLE_FLOOD_IMG = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 350'>"
    "<rect width='600' height='350' fill='%2305141b'/>"
    "<path d='M0,190 Q150,150 300,180 T600,170 L600,350 L0,350 Z' fill='%230284c7' opacity='0.85'/>"
    "<path d='M0,230 Q200,210 400,240 T600,220 L600,350 L0,350 Z' fill='%230369a1'/>"
    "<text x='30' y='50' fill='%2338bdf8' font-family='sans-serif' font-weight='bold' font-size='18'>"
    "🌊 JAL TARANGA GEOTAG PROOF: PADDY BUND SPILLOVER [ALAPPUZHA]"
    "</text>"
    "<text x='30' y='75' fill='%2300E5FF' font-family='monospace' font-size='13'>"
    "COORDINATES: 9.4800 N, 76.3900 E • WATER STAGE: +0.85m MSL"
    "</text>"
    "</svg>"
)

# In-memory operational report database with baseline verification records
_reports_db: List[Dict[str, Any]] = [
    {
        "id": "UY-REP-501",
        "district": "Wayanad",
        "category": "Landslide / Slope Failure",
        "severity": "Critical",
        "timestamp": "2026-09-09 22:30",
        "lat": 11.53,
        "lng": 76.18,
        "location_name": "Meppadi Hill Slopes, Wayanad",
        "reporter_role": "officer",
        "reporter_name": "KSDMA Field Observer",
        "upvotes": 12,
        "desc": "Surface tension cracks observed along road cut. Upper slope saturation active.",
        "email": "ksdma.observer@kerala.gov.in",
        "image": SAMPLE_LANDSLIDE_IMG,
        "status": "Verified",
    },
    {
        "id": "UY-REP-502",
        "district": "Alappuzha",
        "category": "Flood / Water Accumulation",
        "severity": "High",
        "timestamp": "2026-09-09 23:15",
        "lat": 9.48,
        "lng": 76.39,
        "location_name": "Kuttanad Polder Bund, Alappuzha",
        "reporter_role": "citizen",
        "reporter_name": "Pamba River Warden",
        "upvotes": 8,
        "desc": "Water level 0.85m over paddy bund. Pamba backflow hindering drainage.",
        "email": "pamba.warden@kuttanad.org",
        "image": SAMPLE_FLOOD_IMG,
        "status": "In Progress",
    },
]

# Cached datasets
_cached_districts: Optional[List[Dict[str, Any]]] = None
_cached_landmarks: Optional[List[Dict[str, Any]]] = None
_cached_watersheds_data: Optional[Dict[str, Any]] = None
_cached_kerala_boundary: Optional[Dict[str, Any]] = None


def get_kerala_boundary() -> Dict[str, Any]:
    """Retrieve official Kerala state boundary GeoJSON."""
    global _cached_kerala_boundary
    if _cached_kerala_boundary is not None:
        return _cached_kerala_boundary
    file_path = settings.DATA_DIR / "kerala_boundary.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            _cached_kerala_boundary = json.load(f)
            return _cached_kerala_boundary
    return {"type": "FeatureCollection", "features": []}



def get_districts() -> List[Dict[str, Any]]:
    """Retrieve all 14 Kerala districts from PostgreSQL (with fallback to districts.json)."""
    db_districts = get_districts_from_db()
    if db_districts:
        return db_districts

    global _cached_districts
    if _cached_districts is not None:
        return _cached_districts

    file_path = settings.DATA_DIR / "districts.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            _cached_districts = json.load(f)
            return _cached_districts
    return []


def get_landmarks() -> List[Dict[str, Any]]:
    """Retrieve protected infrastructure and restricted landmarks from landmarks.json."""
    global _cached_landmarks
    if _cached_landmarks is not None:
        return _cached_landmarks

    file_path = settings.DATA_DIR / "landmarks.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            _cached_landmarks = json.load(f)
            return _cached_landmarks
    return []


def _load_watersheds_file() -> Dict[str, Any]:
    """Internal helper to load watersheds, inundation, and landslide zones."""
    global _cached_watersheds_data
    if _cached_watersheds_data is not None:
        return _cached_watersheds_data

    file_path = settings.DATA_DIR / "watersheds.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            _cached_watersheds_data = json.load(f)
            return _cached_watersheds_data
    return {"watersheds": [], "inundation_zones": [], "landslide_zones": []}


def get_watersheds() -> List[Dict[str, Any]]:
    """Retrieve major river basin watershed polygons from PostGIS (with fallback to watersheds.json)."""
    db_basins = get_river_basins_from_db()
    if db_basins:
        return db_basins

    data = _load_watersheds_file()
    return data.get("watersheds", [])


def get_inundation_zones() -> List[Dict[str, Any]]:
    """Retrieve documented historical inundation zones."""
    data = _load_watersheds_file()
    return data.get("inundation_zones", [])


def get_landslide_zones() -> List[Dict[str, Any]]:
    """Retrieve high-risk scarp and landslide trigger zones."""
    data = _load_watersheds_file()
    return data.get("landslide_zones", [])


def get_reports_db(
    user_id: Optional[str] = None,
    reporter_role: Optional[str] = None,
    user_ids: Optional[List[str]] = None,
    emails: Optional[List[str]] = None,
    report_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Retrieve all reports for admin review or filtered tracking (from PostgreSQL or fallback)."""
    db_reports = get_citizen_reports_from_db(
        user_id=user_id,
        reporter_role=reporter_role,
        user_ids=user_ids,
        emails=emails,
        report_ids=report_ids
    )
    if db_reports is not None:
        return db_reports
    with _lock:
        res = list(_reports_db)
        if user_id or user_ids or emails or report_ids:
            all_uids = set(user_ids or [])
            if user_id:
                all_uids.add(user_id)
            all_emails = {e.lower().strip() for e in (emails or []) if e}
            if user_id and "@" in user_id:
                all_emails.add(user_id.lower().strip())
            all_rids = set(report_ids or [])

            filtered = []
            for r in res:
                r_uid = r.get("reporter_id") or ""
                r_email = (r.get("email") or r.get("reporter_email") or "").lower().strip()
                r_id = r.get("id") or ""
                if (r_uid and r_uid in all_uids) or (r_email and r_email in all_emails) or (r_id and r_id in all_rids):
                    filtered.append(r)
            res = filtered

        if reporter_role:
            res = [r for r in res if r.get("reporter_role") == reporter_role]
        return res


def get_public_reports_db() -> List[Dict[str, Any]]:
    """
    Retrieve sanitized public feed of incident reports.
    Strictly scrubs all private user information (email, phone, password, user IDs).
    """
    reports = get_reports_db()
    sanitized = []
    for r in reports:
        sanitized.append({
            "id": r["id"],
            "district": r["district"],
            "category": r["category"],
            "severity": r["severity"],
            "timestamp": r.get("timestamp", ""),
            "lat": r["lat"],
            "lng": r["lng"],
            "location_name": r.get("location_name") or f"{r['district']}, India",
            "reporter_role": r.get("reporter_role", "citizen"),
            "reporter_name": r.get("reporter_name", "Citizen Observer"),
            "upvotes": int(r.get("upvotes") or 0),
            "status": r.get("status", "Submitted"),
            "remarks": r.get("remarks", ""),
            "desc": r.get("desc", ""),
            "image": r.get("image"),
        })
    return sanitized


def add_report_to_db(r: Any) -> Dict[str, Any]:
    """Add a new field report to PostgreSQL (fallback to in-memory)."""
    db_entry = add_citizen_report_to_db(r)
    if db_entry:
        return db_entry

    with _lock:
        entry = {
            "id": f"UY-REP-{len(_reports_db) + 501}",
            "district": r.district,
            "category": r.category,
            "severity": r.severity,
            "email": r.email.strip() if hasattr(r, "email") else "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "lat": r.lat,
            "lng": r.lng,
            "desc": r.desc,
            "image": getattr(r, "image", None),
            "location_name": getattr(r, "location_name", None) or f"{r.district}, India",
            "reporter_role": getattr(r, "reporter_role", "citizen") or "citizen",
            "reporter_id": getattr(r, "reporter_id", "") or "",
            "reporter_name": getattr(r, "reporter_name", "Citizen Observer"),
            "upvotes": 0,
            "status": "Submitted",
        }
        _reports_db.insert(0, entry)
        return entry


def update_report_in_db(
    report_id: str,
    new_status: str,
    remarks: Optional[str] = None,
    assigned_to: Optional[str] = None,
    updated_by: Optional[str] = None,
    updated_by_role: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Update status and remarks of a report in PostgreSQL (fallback to in-memory)."""
    db_res = update_citizen_report_status_in_db(
        report_id=report_id,
        new_status=new_status,
        remarks=remarks,
        assigned_to=assigned_to,
        updated_by=updated_by,
        updated_by_role=updated_by_role
    )
    if db_res:
        return db_res

    with _lock:
        for r in _reports_db:
            if r["id"] == report_id:
                r["status"] = new_status
                if remarks: r["remarks"] = remarks
                if assigned_to: r["assigned_to"] = assigned_to
                return dict(r)
        return None


def delete_report_from_db(report_id: str) -> bool:
    """Delete a report by ID from PostgreSQL (fallback to in-memory)."""
    deleted = delete_citizen_report_from_db(report_id)
    if deleted:
        return True

    global _reports_db
    with _lock:
        initial_count = len(_reports_db)
        _reports_db = [r for r in _reports_db if r["id"] != report_id]
        return len(_reports_db) < initial_count

