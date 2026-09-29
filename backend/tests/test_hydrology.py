"""
VELLAM Geospatial Platform - Hydrology & Spatial Unit Tests
Validates geodetic distance calculations, collision detection, and mathematical hydrological solvers.
"""

import sys
from pathlib import Path
import pytest

# Ensure backend root is in sys.path
backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.services.hydrology import (
    haversine_km,
    check_restricted_infrastructure,
    run_microterrain_hydrological_solver,
    compute_water_accumulation,
    simulate_intervention,
)


def test_haversine_distance():
    """Verify haversine formula against known coordinates."""
    # Distance to identical point is 0
    assert haversine_km(10.0, 76.0, 10.0, 76.0) == 0.0

    # Approx distance between Thiruvananthapuram (8.52, 76.93) and Kochi (9.98, 76.28) is ~175-200 km
    d = haversine_km(8.52, 76.93, 9.98, 76.28)
    assert 170.0 <= d <= 210.0


def test_restricted_infrastructure_detection():
    """Verify detection of critical restricted infrastructure."""
    # Technopark Trivandrum at 8.558 N, 76.882 E
    detected = check_restricted_infrastructure(
        north=8.57, south=8.54, east=76.90, west=76.87
    )
    assert detected is not None
    assert "Technopark" in detected["name"]

    # Remote forest region in Silent Valley buffer outside any protected airport/dam buffer
    empty_zone = check_restricted_infrastructure(
        north=11.10, south=11.05, east=76.45, west=76.40
    )
    assert empty_zone is None


def test_microterrain_solvers_zones():
    """Verify micro-terrain solver matches correct physiographic zones."""
    # 1. Wayanad Escarpment
    res_wayanad = run_microterrain_hydrological_solver(
        center_lat=11.60, center_lng=76.15, lat_span=0.08, lng_span=0.08, area_km2=60.0
    )
    assert "Wayanad" in res_wayanad["zone"]
    assert res_wayanad["runoff_coefficient"] == 0.86

    # 2. Idukki Mountain High-Altitude
    res_idukki = run_microterrain_hydrological_solver(
        center_lat=9.90, center_lng=77.05, lat_span=0.08, lng_span=0.08, area_km2=60.0
    )
    assert "Idukki" in res_idukki["zone"]
    assert res_idukki["runoff_coefficient"] == 0.89

    # 3. Kuttanad Polder Delta
    res_kuttanad = run_microterrain_hydrological_solver(
        center_lat=9.45, center_lng=76.40, lat_span=0.05, lng_span=0.05, area_km2=30.0
    )
    assert "Kuttanad" in res_kuttanad["zone"]
    assert res_kuttanad["mean_slope_deg"] == 0.4

    # 4. Greater Kochi Urban Confluence
    res_kochi = run_microterrain_hydrological_solver(
        center_lat=10.02, center_lng=76.30, lat_span=0.05, lng_span=0.05, area_km2=30.0
    )
    assert "Kochi" in res_kochi["zone"]


def test_accumulation_scenarios():
    """Verify rainfall scenario scaling logic."""
    mod = compute_water_accumulation("Moderate", "WS-PERIYAR")
    high = compute_water_accumulation("High", "WS-PERIYAR")
    extreme = compute_water_accumulation("Extreme", "WS-PERIYAR")

    assert mod["accumulated_mcm"] < high["accumulated_mcm"] < extreme["accumulated_mcm"]
    assert mod["inundated_ha"] < high["inundated_ha"] < extreme["inundated_ha"]
    assert mod["velocity_ms"] < high["velocity_ms"] < extreme["velocity_ms"]


def test_intervention_bounds():
    """Verify intervention physics responses within 0% to 100% density."""
    zero_density = simulate_intervention("check_dams", density=0)
    full_density = simulate_intervention("check_dams", density=100)

    assert zero_density["q_reduction_pct"] == 0.0
    assert zero_density["soil_saved"] == 0.0

    assert full_density["q_reduction_pct"] == 38.0
    assert full_density["soil_saved"] > 0
    assert full_density["post_soil"] < zero_density["post_soil"]


def test_intervention_geodetic_stream_snapping_accuracy():
    """Verify >=97% spatial accuracy and correct fluvial stream order placement for interventions."""
    # Test Check Dams in Periyar (mountain headwaters)
    res_periyar = simulate_intervention("check_dams", density=50, watershed_id="WS-PERIYAR")
    assert "structures" in res_periyar
    structures = res_periyar["structures"]
    assert len(structures) > 0

    for st in structures:
        # Spatial bounding box for Kerala
        assert 8.15 <= st["lat"] <= 12.85, f"Lat {st['lat']} out of bounds for Kerala"
        assert 74.85 <= st["lng"] <= 77.55, f"Lng {st['lng']} out of bounds for Kerala"

        # Fluvial accuracy requirement: >= 97.0%
        acc_str = st["accuracy_pct"]
        acc_val = float(acc_str.replace("%", ""))
        assert acc_val >= 97.0, f"Accuracy {acc_val}% below required 97% threshold"

        # Stream order verification for check dams (should be headwater Order 1, 2, or 3)
        assert st["stream_order"] in [1, 2, 3], f"Check dam on invalid stream order {st['stream_order']}"
        assert "Order" in st["stream_order_label"]
        assert st["upstream_area_km2"] > 0
        assert st["reach_length_km"] > 0
        assert st["verification_source"] == "MERIT-Hydro Geo-referenced Fluvial Network"

    # Test Subsurface Dykes in Bharathapuzha (alluvial sandy riverbed)
    res_bharatha = simulate_intervention("subsurface_dykes", density=60, watershed_id="WS-BHARATHA")
    dykes = res_bharatha["structures"]
    assert len(dykes) > 0
    for dyke in dykes:
        acc_val = float(dyke["accuracy_pct"].replace("%", ""))
        assert acc_val >= 97.0
        # Dykes target wide alluvial channels (Order 3, 4, 5)
        assert dyke["stream_order"] in [3, 4, 5]
        assert dyke["terrain_zone"] == "Alluvial Sandy Riverbed Channel"

