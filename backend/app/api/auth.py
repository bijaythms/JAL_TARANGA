"""
Jal Taranga — Authentication & Role-Segregated Portals API Router
Provides dedicated endpoints and database stores for:
  - Officers (/api/auth/officer-login)
  - Citizens (/api/auth/citizen-login, /api/auth/citizen-register)
  - Administrators (/api/auth/admin-login)
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Header

from app.schemas.models import (
    UserLoginRequest,
    UserRegisterRequest,
    CitizenRegisterRequest,
    AdminLoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    AuthResponse,
    UserProfile,
)
from app.core.user_store import (
    authenticate_officer,
    authenticate_citizen,
    register_citizen,
    authenticate_admin_direct,
    authenticate_user,
    register_user,
    create_password_reset_token,
    apply_password_reset,
    generate_session_token,
    get_user_by_id,
    get_database_stats,
    save_persistent_session,
    load_persistent_sessions,
    delete_persistent_session,
)
from app.core.database import (
    save_session_to_db,
    get_user_id_by_session_db,
    delete_session_from_db,
)

router = APIRouter(prefix="/api/auth", tags=["User Authentication"])

# In-memory session token store (token -> user_id) initialized from persistent store
_ACTIVE_SESSIONS: dict[str, str] = load_persistent_sessions()


def _record_active_session(token: str, user_id: str):
    """Records session in memory, JSON store, and PostgreSQL."""
    _ACTIVE_SESSIONS[token] = user_id
    save_persistent_session(token, user_id)
    save_session_to_db(token, user_id)


def _remove_active_session(token: str):
    """Purges session from memory, JSON store, and PostgreSQL."""
    _ACTIVE_SESSIONS.pop(token, None)
    delete_persistent_session(token)
    delete_session_from_db(token)


def _get_current_user_from_token(token: Optional[str]) -> Optional[dict]:
    """Resolves active user from bearer token across all three database stores."""
    if not token:
        return None
    clean_token = token.replace("Bearer ", "").strip()
    user_id = _ACTIVE_SESSIONS.get(clean_token)
    if not user_id:
        user_id = get_user_id_by_session_db(clean_token)
        if not user_id:
            persistent = load_persistent_sessions()
            user_id = persistent.get(clean_token)
        if user_id:
            _ACTIVE_SESSIONS[clean_token] = user_id

    if user_id:
        return get_user_by_id(user_id)
    return None


def _build_user_profile(user: dict) -> UserProfile:
    return UserProfile(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        role=user.get("role", "analyst"),
        phone=user.get("phone"),
        district=user.get("district"),
        designation=user.get("designation"),
        department=user.get("department"),
        is_active=user.get("is_active", True),
        created_at=user.get("created_at"),
        last_login=user.get("last_login")
    )


# ==============================================================================
# 1. OFFICER PORTAL ENDPOINTS
# ==============================================================================

@router.post("/officer-login", response_model=AuthResponse)
def officer_login(req: UserLoginRequest):
    """
    Dedicated Officer Portal Authentication.
    Validates exclusively against the Officers Database (officers.json).
    Restricted to KSDMA officers, hydrologists, GIS analysts, and field commanders.
    """
    officer = authenticate_officer(req.identifier, req.password)
    if not officer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Officer authorization failed. Invalid official credentials or unverified officer profile."
        )

    token = generate_session_token(officer)
    _record_active_session(token, officer["id"])

    return AuthResponse(
        success=True,
        message=f"Welcome back Officer {officer.get('full_name', officer['username'])}! Accessing Operational Command Dashboards.",
        token=token,
        user=_build_user_profile(officer)
    )


# ==============================================================================
# 2. CITIZEN PORTAL ENDPOINTS
# ==============================================================================

@router.post("/citizen-login", response_model=AuthResponse)
def citizen_login(req: UserLoginRequest):
    """
    Dedicated Citizen Portal Authentication.
    Validates exclusively against the Citizens Database (citizens.json).
    Directs community members directly to the Ground Incident / Hazard Reporting page.
    """
    citizen = authenticate_citizen(req.identifier, req.password)
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Citizen sign in failed. Check your registered phone/email/username or create a new citizen account."
        )

    token = generate_session_token(citizen)
    _record_active_session(token, citizen["id"])

    return AuthResponse(
        success=True,
        message=f"Welcome {citizen.get('full_name', citizen['username'])}! Proceeding to Citizen Field Incident Reporting.",
        token=token,
        user=_build_user_profile(citizen)
    )


@router.post("/citizen-register", response_model=AuthResponse)
def citizen_register(req: CitizenRegisterRequest):
    """
    Dedicated Citizen Registration Endpoint.
    Stores new community members directly into the isolated Citizens Database (citizens.json).
    """
    success, msg, new_citizen = register_citizen(
        username=req.username,
        email=req.email,
        full_name=req.full_name,
        password=req.password,
        phone=req.phone,
        district=req.district
    )

    if not success or not new_citizen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

    token = generate_session_token(new_citizen)
    _record_active_session(token, new_citizen["id"])

    return AuthResponse(
        success=True,
        message="Citizen account created successfully! Proceeding to Field Incident Reporting.",
        token=token,
        user=_build_user_profile(new_citizen)
    )


# ==============================================================================
# 3. ADMIN PORTAL ENDPOINTS
# ==============================================================================

@router.post("/admin-login", response_model=AuthResponse)
def admin_login(req: AdminLoginRequest):
    """
    Unified Admin & Staff Portal authentication.
    Accepts Master Administrator Secret Key, Administrator credentials,
    or official Officer/Analyst credentials.
    """
    staff_user = authenticate_admin_direct(req.admin_key, req.username)
    if not staff_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authorization rejected. Invalid Administrative Key or Officer Credentials."
        )

    token = generate_session_token(staff_user)
    _record_active_session(token, staff_user["id"])

    role_title = "Administrator" if staff_user.get("role") == "admin" else "Officer"
    return AuthResponse(
        success=True,
        message=f"{role_title} Command Access Authorized. Welcome {staff_user.get('full_name', staff_user['username'])}!",
        token=token,
        user=_build_user_profile(staff_user)
    )


# ==============================================================================
# 4. STANDARD & BACKWARD-COMPATIBLE ENDPOINTS
# ==============================================================================

@router.post("/login", response_model=AuthResponse)
def login(req: UserLoginRequest):
    """
    Standard user login.
    Checks Officers DB first, then Citizens DB.
    """
    user = authenticate_user(req.identifier, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please check your username/email and password."
        )

    token = generate_session_token(user)
    _record_active_session(token, user["id"])

    return AuthResponse(
        success=True,
        message=f"Welcome back, {user.get('full_name', user['username'])}!",
        token=token,
        user=_build_user_profile(user)
    )


@router.post("/register", response_model=AuthResponse)
def register(req: UserRegisterRequest):
    """
    General registration endpoint.
    Routes citizen accounts to citizens.json and departmental accounts to officers.json.
    """
    success, msg, new_user = register_user(
        username=req.username,
        email=req.email,
        full_name=req.full_name,
        password=req.password,
        role=req.role or "analyst",
        phone=req.phone,
        district=req.district
    )

    if not success or not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

    token = generate_session_token(new_user)
    _record_active_session(token, new_user["id"])

    return AuthResponse(
        success=True,
        message="Account created successfully. Welcome to Jal Taranga!",
        token=token,
        user=_build_user_profile(new_user)
    )


@router.get("/me", response_model=AuthResponse)
def get_current_user(authorization: Optional[str] = Header(None)):
    """Session verification endpoint. Resolves current user from bearer token."""
    user = _get_current_user_from_token(authorization)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or unauthorized. Please sign in again."
        )

    return AuthResponse(
        success=True,
        message="Session active",
        token=authorization.replace("Bearer ", "").strip() if authorization else None,
        user=_build_user_profile(user)
    )


@router.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    """Terminates active session token across memory, JSON store, and database."""
    if authorization:
        clean_token = authorization.replace("Bearer ", "").strip()
        _remove_active_session(clean_token)
    return {"success": True, "message": "Logged out successfully"}


@router.get("/stores-status")
def stores_status():
    """Diagnostic status showing that 3 separate databases are maintained independently."""
    return {
        "status": "online",
        "segregation": "3-tier isolated databases",
        "data": get_database_stats()
    }


# ==============================================================================
# 5. PASSWORD RECOVERY & RESET ENDPOINTS
# ==============================================================================

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    """
    Initiates password recovery for Admin/Officer or Citizen.
    Generates a secure verification code and returns recovery details.
    """
    success, msg, data = create_password_reset_token(req.identifier, req.role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg
        )
    return {
        "success": True,
        "message": msg,
        "token": data.get("token") if data else None,
        "masked_email": data.get("masked_email") if data else None,
        "tier": data.get("tier") if data else None,
        "username": data.get("username") if data else None
    }


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest):
    """
    Applies new password using verified token.
    Updates the database table (administrators, officers, or citizens) and invalidates old sessions.
    """
    success, msg = apply_password_reset(req.token, req.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )
    return {
        "success": True,
        "message": msg
    }

