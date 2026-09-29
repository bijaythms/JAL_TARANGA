"""
JAL TARANGA — Authentication & Role-Segregation Tests
Validates:
  1. Dedicated Officer Portal (/api/auth/officer-login) against Officers DB
  2. Dedicated Citizen Portal (/api/auth/citizen-login & /api/auth/citizen-register) against Citizens DB
  3. Dedicated Admin Portal (/api/auth/admin-login) against Admins DB
  4. Cross-database isolation (officers cannot enter via citizen endpoint, and vice versa)
  5. Stores status endpoint confirming 3-tier database isolation
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.user_store import load_officers, load_citizens, load_admins

client = TestClient(app)


def test_officer_login_success():
    """Validates that seeded officer can log in successfully via the officer portal."""
    payload = {
        "identifier": "bijay",
        "password": "user123",
        "remember_me": False
    }
    res = client.post("/api/auth/officer-login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["username"] == "bijay"
    assert data["user"]["role"] in ["analyst", "officer"]


def test_officer_login_invalid_password():
    """Validates rejection of incorrect officer password."""
    payload = {
        "identifier": "bijay",
        "password": "wrong_password_999",
        "remember_me": False
    }
    res = client.post("/api/auth/officer-login", json=payload)
    assert res.status_code == 401


def test_officer_login_rejects_citizen():
    """Ensures a citizen cannot log in via the official Officer portal."""
    payload = {
        "identifier": "citizen1",
        "password": "citizen123"
    }
    res = client.post("/api/auth/officer-login", json=payload)
    assert res.status_code == 401


def test_citizen_login_success():
    """Validates that registered citizen can log in via citizen portal."""
    payload = {
        "identifier": "citizen1",
        "password": "citizen123"
    }
    res = client.post("/api/auth/citizen-login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["user"]["role"] == "citizen"
    assert data["user"]["district"] == "Wayanad"


def test_citizen_login_rejects_officer():
    """Ensures an officer cannot log in via the Citizen portal."""
    payload = {
        "identifier": "bijay",
        "password": "user123"
    }
    res = client.post("/api/auth/citizen-login", json=payload)
    assert res.status_code == 401


def test_citizen_registration_and_login():
    """Validates registering a new citizen into the Citizens database and authenticating."""
    test_username = "sunil_observer"
    test_email = "sunil.observer@gmail.com"
    test_pwd = "safe_kerala_2026"
    
    reg_payload = {
        "full_name": "Sunil Kumar",
        "email": test_email,
        "username": test_username,
        "password": test_pwd,
        "phone": "+91-9447123456",
        "district": "Idukki"
    }
    
    # 1. Register new citizen
    res = client.post("/api/auth/citizen-register", json=reg_payload)
    assert res.status_code in [200, 400]  # 400 if already created in earlier test run
    
    # 2. Login via citizen portal
    login_res = client.post("/api/auth/citizen-login", json={"identifier": test_username, "password": test_pwd})
    assert login_res.status_code == 200
    user_data = login_res.json()
    assert user_data["user"]["role"] == "citizen"
    assert user_data["user"]["full_name"] == "Sunil Kumar"
    assert user_data["user"]["district"] == "Idukki"


def test_separated_admin_login_success():
    """Validates dedicated admin authentication with administrative secret key."""
    payload = {
        "admin_key": "VIP@DUK",
        "username": "admin"
    }
    res = client.post("/api/auth/admin-login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["user"]["role"] == "admin"
    assert "token" in data


def test_separated_admin_login_invalid_key():
    """Validates that wrong secret key is rejected with 403 Forbidden."""
    payload = {
        "admin_key": "invalid-secret-key-xyz",
        "username": "admin"
    }
    res = client.post("/api/auth/admin-login", json=payload)
    assert res.status_code == 403


def test_stores_status_segregation():
    """Verifies that stores status returns 3 separate databases and non-zero counts."""
    res = client.get("/api/auth/stores-status")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "online"
    stats = body["data"]
    assert stats["officers_count"] >= 1
    assert stats["citizens_count"] >= 1
    assert stats["admins_count"] >= 1
    assert "officers_db" in stats["stores"]
    assert "citizens_db" in stats["stores"]
    assert "admins_db" in stats["stores"]


def test_session_me_and_logout():
    """Validates token-based session resolution and logout across stores."""
    # 1. Login
    login_res = client.post("/api/auth/officer-login", json={"identifier": "bijay", "password": "user123"})
    token = login_res.json()["token"]
    
    # 2. Check /me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["user"]["username"] == "bijay"
    
    # 3. Logout
    logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200
    assert logout_res.json()["success"] is True
    
    # 4. Check /me after logout (should fail 401)
    me_after = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_after.status_code == 401


def test_unified_admin_login_with_officer_credentials():
    """Validates that existing officer accounts can log in via the unified Admin portal."""
    payload = {
        "admin_key": "user123",
        "username": "bijay"
    }
    res = client.post("/api/auth/admin-login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["user"]["username"] == "bijay"
    assert data["user"]["role"] in ["analyst", "officer"]
    assert "token" in data


def test_unified_admin_login_rejects_citizen():
    """Ensures citizens cannot access the unified Admin & Staff portal."""
    payload = {
        "admin_key": "citizen123",
        "username": "citizen1"
    }
    res = client.post("/api/auth/admin-login", json=payload)
    assert res.status_code == 403

