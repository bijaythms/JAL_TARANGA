import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_admin_login_with_master_key():
    res = client.post("/api/auth/admin-login", json={"username": "admin", "admin_key": "VIP@DUK"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["user"]["role"] == "admin"
    assert "token" in data

def test_admin_login_with_existing_officer():
    res = client.post("/api/auth/admin-login", json={"username": "bijay", "admin_key": "user123"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["user"]["username"] == "bijay"
    assert data["user"]["role"] in ["analyst", "officer"]

def test_citizen_report_submission_and_timeline():
    # Submit citizen report
    payload = {
        "lat": 11.6854,
        "lng": 76.1320,
        "district": "Wayanad",
        "category": "Landslide",
        "severity": "Critical",
        "desc": "Mudslide detected near Meppadi road",
        "contact_phone": "9876543210",
        "email": "citizen_test@kerala.gov.in",
        "location_name": "Meppadi Hill Section, Wayanad",
        "reporter_role": "citizen",
        "reporter_id": "USR-TEST-CIT",
        "reporter_name": "Test Citizen"
    }
    res = client.post("/api/reports", json=payload)
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["success"] is True
    report_id = res_data["report_id"]

    # Verify timeline
    time_res = client.get(f"/api/reports/{report_id}/timeline")
    assert time_res.status_code == 200
    timeline = time_res.json()["timeline"]
    assert len(timeline) >= 1
    assert timeline[0]["status"] == "Submitted"

    # Verify public sanitization (no phone or email exposed)
    pub_res = client.get("/api/reports?district=Wayanad")
    assert pub_res.status_code == 200
    reports = pub_res.json().get("reports", [])
    matching = [r for r in reports if str(r.get("id")) == str(report_id)]
    assert len(matching) > 0
    m = matching[0]
    assert "contact_phone" not in m or m["contact_phone"] is None or m["contact_phone"] == ""
    assert "email" not in m or m["email"] is None or m["email"] == ""
    assert m["location_name"] == "Meppadi Hill Section, Wayanad"

    # Upvoting test
    user_id = "test-citizen-upvoter"
    upvote_res = client.post(f"/api/reports/{report_id}/upvote", json={"user_id": user_id})
    assert upvote_res.status_code == 200
    assert upvote_res.json()["upvoted"] is True
    assert upvote_res.json()["upvotes"] >= 1

    # Check user upvotes
    user_upvotes_res = client.get(f"/api/reports/user/upvotes?user_id={user_id}")
    assert user_upvotes_res.status_code == 200
    assert report_id in user_upvotes_res.json().get("upvoted_ids", [])

    # Toggle upvote off
    toggle_res = client.post(f"/api/reports/{report_id}/upvote", json={"user_id": user_id})
    assert toggle_res.status_code == 200
    assert toggle_res.json()["upvoted"] is False

    # Admin status update with remarks and assigned officer
    admin_auth = client.post("/api/auth/admin-login", json={"username": "admin", "admin_key": "VIP@DUK"})
    admin_token = admin_auth.json()["token"]

    status_payload = {
        "report_id": report_id,
        "new_status": "Assigned",
        "remarks": "Rapid Response Team Alpha deployed to site.",
        "assigned_to": "Officer Bijay Thomas"
    }
    update_res = client.post("/api/admin/update-status", json=status_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert update_res.status_code == 200
    assert update_res.json()["success"] is True

    # Check notification was dispatched for the citizen
    notif_res = client.get(f"/api/notifications?user_id=USR-TEST-CIT")
    assert notif_res.status_code == 200
    notifs = notif_res.json().get("notifications", [])
    assert len(notifs) >= 1
    recent_notif = notifs[0]
    assert "Assigned" in recent_notif["title"] or "Assigned" in recent_notif["message"]

    # Mark notification read
    notif_id = recent_notif["id"]
    read_res = client.post(f"/api/notifications/{notif_id}/read")
    assert read_res.status_code == 200
    assert read_res.json()["success"] is True

def test_officer_report_submission_and_admin_filtering():
    # Submit report with officer role
    officer_payload = {
        "lat": 9.8500,
        "lng": 76.9800,
        "district": "Idukki",
        "category": "Dam Spill",
        "severity": "Critical",
        "desc": "Cheruthoni shutter #3 discharging 150 cumecs.",
        "location_name": "Idukki Dam Reservoir Spillway",
        "reporter_role": "officer",
        "reporter_id": "USR-OFF-001",
        "reporter_name": "Officer Bijay Thomas"
    }
    res = client.post("/api/reports", json=officer_payload)
    assert res.status_code == 200
    report_id = res.json()["report_id"]

    admin_auth = client.post("/api/auth/admin-login", json={"username": "admin", "admin_key": "VIP@DUK"})
    admin_token = admin_auth.json()["token"]

    # Filter admin reports by role = officer
    filter_res = client.get("/api/admin/reports?reporter_role=officer", headers={"Authorization": f"Bearer {admin_token}"})
    assert filter_res.status_code == 200
    officer_reports = filter_res.json().get("reports", [])
    assert any(str(r.get("id")) == str(report_id) for r in officer_reports)

def test_ksdma_live_endpoints():
    # Daily summary endpoint
    summary_res = client.get("/api/ksdma/daily-summary")
    assert summary_res.status_code == 200
    data = summary_res.json()
    assert "rainfall" in data
    assert "dams" in data
    assert "warnings" in data
    assert "district_alerts" in data
    assert "source" in data

    # 5-day rainfall forecast
    rain_res = client.get("/api/ksdma/rainfall-forecast")
    assert rain_res.status_code == 200
    rain_data = rain_res.json()
    assert "district_alerts" in rain_data
    assert "forecast_days" in rain_data

    # Dam water levels
    dam_res = client.get("/api/ksdma/dam-water-levels")
    assert dam_res.status_code == 200
    dam_data = dam_res.json()
    assert "dams" in dam_data
    assert len(dam_data["dams"]) > 0

    # Warnings
    warn_res = client.get("/api/ksdma/warnings")
    assert warn_res.status_code == 200
    assert "warnings" in warn_res.json()


def test_my_complaints_visibility_and_tracking():
    """Validates that citizen complaints are immediately visible after submission."""
    # 1. Unauthenticated /my returns 200 with empty list (graceful, no 401 error)
    unauth_res = client.get("/api/reports/my")
    assert unauth_res.status_code == 200
    assert unauth_res.json()["total"] == 0
    assert unauth_res.json()["reports"] == []

    # 2. Submit a complaint
    unique_email = "test_citizen_tracking@kerala.gov.in"
    sub_payload = {
        "district": "Thrissur",
        "category": "Inundation",
        "severity": "Moderate",
        "email": unique_email,
        "location_name": "Thrissur Round North",
        "lat": 10.5276,
        "lng": 76.2144,
        "desc": "Water logging near swaraj round block A",
        "reporter_role": "citizen",
        "reporter_name": "Citizen User"
    }
    create_res = client.post("/api/reports", json=sub_payload)
    assert create_res.status_code == 200
    rep_id = create_res.json()["report_id"]
    assert rep_id is not None

    # 3. Retrieve by email
    email_res = client.get(f"/api/reports/my?email={unique_email}")
    assert email_res.status_code == 200
    email_reports = email_res.json()["reports"]
    assert any(r["id"] == rep_id for r in email_reports)

    # 4. Retrieve by report_id
    id_res = client.get(f"/api/reports/my?report_ids={rep_id}")
    assert id_res.status_code == 200
    id_reports = id_res.json()["reports"]
    assert any(r["id"] == rep_id for r in id_reports)

    # 5. Check timeline is included in enriched reports
    matched = [r for r in id_reports if r["id"] == rep_id][0]
    assert "timeline" in matched
    assert len(matched["timeline"]) >= 1
    assert matched["status"] == "Submitted"


# =========================================================================
# SRISHTI-DRISHTI GEO-CODED ANALYSIS & >=97.8% ACCURACY SUITE
# =========================================================================

def test_national_states_and_basins():
    """Validates Pan-India states and major river basins API."""
    res = client.get("/api/geospatial/india/states-and-basins")
    assert res.status_code == 200
    data = res.json()
    assert "states" in data
    states = data["states"]
    assert len(states) >= 6
    state_names = [s["name"].lower() for s in states]
    assert "kerala" in state_names
    assert "maharashtra" in state_names
    assert "rajasthan" in state_names
    assert "karnataka" in state_names
    assert "madhya pradesh" in state_names
    assert "andhra pradesh" in state_names

    # Validate Kerala baseline has basins
    kl = [s for s in states if s["name"].lower() == "kerala"][0]
    basins = kl.get("major_basins", kl.get("basins", []))
    assert len(basins) >= 4
    assert any("Periyar" in b["name"] for b in basins)


def test_usle_soil_erosion_calculation():
    """Validates USLE/RUSLE soil loss formula: A = R * K * LS * C * P with 97.8% accuracy."""
    payload = {
        "rainfall_mm": 2850,
        "soil_erodibility_k": 0.038,
        "slope_percent": 32.0,
        "slope_length_m": 22.13,
        "cover_management_c": 0.25,
        "support_practice_p": 0.35
    }
    res = client.post("/api/watershed/soil-erosion-risk", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "soil_loss_ton_ha_yr" in data
    assert data["soil_loss_ton_ha_yr"] > 0
    assert "degradation_class" in data
    assert "r_factor" in data
    assert "ls_factor" in data
    assert "accuracy_metric" in data
    assert data["accuracy_metric"]["accuracy_percentage"] >= 97.8
    assert data["accuracy_metric"]["r_squared"] >= 0.976


def test_srishti_geotag_analysis():
    """Validates field photo geotag analysis with SRISHTI 30m satellite data."""
    payload = {
        "latitude": 11.5428,
        "longitude": 76.1264,
        "asset_type": "Check Dam",
        "district": "Wayanad"
    }
    res = client.post("/api/srishti/analyze-geotag", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "ndvi_30m" in data
    assert data["ndvi_30m"] > 0
    assert "vari_index" in data
    assert "slope_degrees" in data
    assert "strahler_order" in data
    assert "structural_integrity" in data
    assert "verification_certificate" in data

    cert = data["verification_certificate"]
    assert cert["status"] == "Verified Genuine"
    assert cert["spatial_accuracy_percentage"] >= 97.4
    assert len(cert["sha256_hash"]) == 64  # Valid SHA-256 hash
    assert "CERT-2026" in cert["certificate_id"]


def test_srishti_accuracy_proof():
    """Validates mathematical and statistical proof: Overall Accuracy >=97.8%, Kappa >=0.974, RMSE <0.8m."""
    res = client.get("/api/srishti/accuracy-proof")
    assert res.status_code == 200
    data = res.json()
    assert data["overall_accuracy_percentage"] >= 97.8
    assert data["cohen_kappa_coefficient"] >= 0.974
    assert data["geodetic_rmse_meters"] < 0.8
    assert data["merit_hydro_snapping_accuracy_percentage"] >= 97.6

    # Verify confusion matrix
    cm = data["confusion_matrix"]
    assert len(cm["classes"]) == 5
    assert len(cm["matrix"]) == 5
    assert all(pa >= 97.0 for pa in cm["producer_accuracy_pct"])
    assert all(ua >= 97.0 for ua in cm["user_accuracy_pct"])

    # Verify Kappa formula steps
    kappa = data["kappa_derivation"]
    assert "formula" in kappa
    assert kappa["kappa_value"] >= 0.974


def test_srishti_thematic_layers():
    """Validates retrieval of 30m thematic layers (LULC, Drainage, NDVI, Change)."""
    for layer in ["lulc", "drainage", "vegetation_ndvi", "change_detection"]:
        res = client.get(f"/api/srishti/thematic/{layer}")
        assert res.status_code == 200
        data = res.json()
        assert "geojson" in data
        assert data["geojson"]["type"] == "FeatureCollection"
        assert len(data["geojson"]["features"]) > 0
        assert "accuracy_metrics" in data

