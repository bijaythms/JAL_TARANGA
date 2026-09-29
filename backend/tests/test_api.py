"""
VELLAM Geospatial Platform - API Integration Tests
Validates all REST API endpoints using FastAPI TestClient.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_health_check():
    """Verify system health endpoint returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_get_baseline():
    """Verify scientific baseline returns all 14 districts and 4 watersheds."""
    response = client.get("/api/kerala/baseline")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["districts"]) == 14
    assert len(data["watersheds"]) >= 4
    assert len(data["inundation_zones"]) >= 3
    assert len(data["landslide_zones"]) >= 3


def test_srishti_api():
    """Verify ISRO Bhuvan Srishti & Drishti assets and analytics endpoints."""
    res_assets = client.get("/api/srishti/assets")
    assert res_assets.status_code == 200
    assets_data = res_assets.json()
    assert "assets" in assets_data
    assert len(assets_data["assets"]) >= 6

    res_ana = client.get("/api/srishti/analytics")
    assert res_ana.status_code == 200
    ana_data = res_ana.json()
    assert ana_data["total_assets"] >= 6
    assert ana_data["total_storage_capacity_m3"] > 0


def test_admin_verify_key():
    """Verify administrator secret key validation (success and rejection)."""
    # Success with correct key
    valid_resp = client.post("/api/admin/verify", json={"key": settings.ADMIN_SECRET_KEY})
    assert valid_resp.status_code == 200
    assert valid_resp.json()["authenticated"] is True

    # Rejection with invalid key
    invalid_resp = client.post("/api/admin/verify", json={"key": "WRONG_SECRET_KEY"})
    assert invalid_resp.status_code == 200
    assert invalid_resp.json()["authenticated"] is False


def test_reports_lifecycle():
    """Verify submitting a report, reading public feed, updating status, and deleting report."""
    # 1. Submit a new report
    new_report = {
        "district": "Idukki",
        "category": "Landslide / Slope Failure",
        "severity": "High",
        "email": "tester@ksdma.gov.in",
        "lat": 9.92,
        "lng": 77.10,
        "desc": "Fresh rill erosion observed along hill terrace.",
    }
    create_resp = client.post("/api/reports", json=new_report)
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["status"] == "success"
    rep_id = created["data"]["id"]

    # 2. Verify it appears in public feed without exposing email
    public_resp = client.get("/api/reports")
    assert public_resp.status_code == 200
    pub_data = public_resp.json()
    assert pub_data["total"] >= 1
    found = next((r for r in pub_data["reports"] if r["id"] == rep_id), None)
    assert found is not None
    assert "email" not in found

    # 3. Update report status via admin endpoint
    update_resp = client.post(
        "/api/admin/update-status",
        json={"report_id": rep_id, "status": "Action Initiated"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["updated"]["status"] == "Action Initiated"

    # 4. Purge the report
    del_resp = client.post("/api/admin/delete-report", json={"report_id": rep_id})
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "success"


def test_dem_accumulation_simulation():
    """Verify DEM rainfall surface accumulation calculator."""
    payload = {"scenario": "Extreme", "watershed_id": "WS-PERIYAR"}
    response = client.post("/api/dem/accumulation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scenario"] == "Extreme"
    assert data["accumulated_mcm"] > 0
    assert data["inundated_ha"] > 0
    assert data["velocity_ms"] > 0


def test_intervention_simulation():
    """Verify watershed intervention simulation physics."""
    payload = {"intervention_type": "check_dams", "density": 80}
    response = client.post("/api/intervention/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["density"] == 80
    assert data["q_reduction_pct"] > 0
    assert data["soil_saved"] > 0
    assert data["post_rech"] > 0


def test_watershed_ai_plan_restricted():
    """Verify restricted infrastructure boundary protection (e.g. Cochin Airport)."""
    # Coordinates bounding Cochin International Airport (10.155 N, 76.402 E)
    payload = {
        "north": 10.165,
        "south": 10.145,
        "east": 76.415,
        "west": 76.390,
    }
    response = client.post("/api/watershed/ai-plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "restricted"
    assert data["is_restricted_property"] is True
    assert "Cochin International Airport" in data["landmark_name"]


def test_watershed_ai_plan_unrestricted():
    """Verify micro-terrain solver returns scientific measures for unrestricted area."""
    # Coordinates in Wayanad catchment
    payload = {
        "north": 11.60,
        "south": 11.50,
        "east": 76.20,
        "west": 76.10,
    }
    response = client.post("/api/watershed/ai-plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["is_restricted_property"] is False
    assert len(data["scientific_measures"]) == 4
    assert data["expected_outcomes"]["discharge_reduction_pct"] > 0


def test_srishti_api():
    """Verify ISRO Srishti & Drishti endpoints for asset registry and analytics."""
    # 1. Test get assets
    res = client.get("/api/srishti/assets")
    assert res.status_code == 200
    data = res.json()
    assert "assets" in data
    assert len(data["assets"]) >= 7
    # Verify assets have authentic local watershed images
    assert any("/images/watershed/" in a.get("photo_before", "") for a in data["assets"])

    # 2. Test analytics
    res_analytics = client.get("/api/srishti/analytics")
    assert res_analytics.status_code == 200
    analytics = res_analytics.json()
    assert analytics["total_assets"] >= 7
    assert analytics["total_storage_capacity_m3"] > 0

    # 3. Test asset creation
    new_asset = {
        "name": "Meppadi Test Gully Plug",
        "category": "Soil & Moisture Conservation",
        "district": "Wayanad",
        "lat": 11.5428,
        "lng": 76.1264,
        "azimuth_deg": 180,
    }
    res_create = client.post("/api/srishti/assets", json=new_asset)
    assert res_create.status_code == 201
    created = res_create.json()
    assert created["status"] == "success"
    assert "DRISHTI-KL-FLD-" in created["asset"]["id"]
    assert "/api/srishti/satellite-crop" in created["asset"]["photo_before"] or "/images/watershed/" in created["asset"]["photo_before"]


def test_srishti_satellite_crop():
    """Verify dynamic satellite-crop endpoint serves valid JPEG images."""
    res_truecolor = client.get("/api/srishti/satellite-crop?lat=11.5428&lng=76.1264&mode=truecolor")
    assert res_truecolor.status_code == 200
    assert res_truecolor.headers["content-type"] == "image/jpeg"
    assert len(res_truecolor.content) > 5000

    res_ndvi = client.get("/api/srishti/satellite-crop?lat=11.5428&lng=76.1264&mode=ndvi")
    assert res_ndvi.status_code == 200
    assert res_ndvi.headers["content-type"] == "image/jpeg"
    assert len(res_ndvi.content) > 5000


def test_landslides_hazards():
    """Verify Western Ghats landslide hazard zones endpoint."""
    res = client.get("/api/landslides/hazards")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["total_monitored"] >= 7
    assert data["critical_count"] >= 3
    assert data["mean_fs"] > 0
    # verify at least one critical zone like Chooralmala
    assert any("Chooralmala" in z["name"] for z in data["zones"])


def test_landslides_simulate_slope():
    """Verify Taylor Infinite Slope Stability geotechnical simulation endpoint."""
    # Test high failure scenario (Chooralmala monsoonal burst)
    payload_crit = {
        "slope_deg": 34.2,
        "saturation_pct": 92.0,
        "depth_m": 2.6,
        "root_cohesion_kpa": 2.0,
    }
    res_crit = client.post("/api/landslides/simulate-slope", json=payload_crit)
    assert res_crit.status_code == 200
    data_crit = res_crit.json()
    assert data_crit["status"] == "success"
    assert data_crit["factor_of_safety"] < 1.0
    assert data_crit["safety_status"] == "CRITICAL_FAILURE_IMMINENT"

    # Test reinforced bio-anchor scenario (Vetiver addition)
    payload_safe = {
        "slope_deg": 34.2,
        "saturation_pct": 92.0,
        "depth_m": 2.6,
        "root_cohesion_kpa": 22.0,
    }
    res_safe = client.post("/api/landslides/simulate-slope", json=payload_safe)
    assert res_safe.status_code == 200
    data_safe = res_safe.json()
    assert data_safe["factor_of_safety"] > 1.3
    assert data_safe["safety_status"] == "GEOTECHNICALLY_STABLE"


