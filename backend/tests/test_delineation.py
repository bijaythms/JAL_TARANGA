"""
VELLAM Geospatial Platform - Interactive Watershed Delineator Tests
Tests the REST API endpoints and service wrapper for mheberger/delineator.
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

client = TestClient(app)


def test_delineate_status_endpoint():
    """Verify delineation status endpoint returns cache info."""
    response = client.get("/api/watershed/delineate/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "cache_info" in data
    assert data["cache_info"]["megabasin"] == 45
    assert "fast_vector_ready" in data["cache_info"]


def test_delineate_invalid_coordinates():
    """Verify validation handles invalid coordinate values."""
    response = client.post(
        "/api/watershed/delineate",
        json={"lat": 999.0, "lng": 76.0},
    )
    assert response.status_code == 422  # Pydantic validation error ge/le


def test_delineate_ocean_point():
    """Verify points in ocean or outside basins return not_found status."""
    response = client.post(
        "/api/watershed/delineate",
        json={"lat": 0.0, "lng": 0.0, "high_res": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("not_found", "error")


def test_delineate_bundled_sample():
    """
    Verify delineation on the bundled Iceland sample (63.938, -21.004).
    This executes 100% offline using the packaged dataset.
    """
    response = client.post(
        "/api/watershed/delineate",
        json={
            "lat": 63.938,
            "lng": -21.004,
            "high_res": False,
            "rivers": True,
            "snap": True,
            "smooth": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["area_km2"] > 5000.0
    assert data["watershed"] is not None
    assert data["watershed"]["type"] == "FeatureCollection"
    assert len(data["watershed"]["features"]) >= 1
    assert data["rivers"] is not None
    assert data["rivers"]["type"] == "FeatureCollection"
    assert data["reach_count"] > 0
    assert data["snapped_point"] is not None
    assert "provenance" in data
