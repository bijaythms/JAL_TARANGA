"""
VELLAM Geospatial Platform - Pydantic Request & Response Schemas
Provides data validation, typing, and OpenAPI documentation schemas.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------
# Admin Authentication Schemas
# ---------------------------------------------------------------------
class AdminAuthRequest(BaseModel):
    key: str = Field(..., description="Administrator secret key string")


class AdminAuthResponse(BaseModel):
    authenticated: bool
    message: str


# ---------------------------------------------------------------------
# User Authentication & Registration Schemas
# ---------------------------------------------------------------------
class UserLoginRequest(BaseModel):
    identifier: str = Field(..., description="Username or email address")
    password: str = Field(..., description="User password")
    remember_me: Optional[bool] = Field(default=False, description="Remember session on this device")


class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, description="User's full name")
    email: str = Field(..., description="Valid email address")
    username: str = Field(..., min_length=3, description="Desired unique username")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    role: Optional[str] = Field(default="analyst", description="Role: 'analyst', 'researcher', or 'citizen'")
    phone: Optional[str] = Field(default=None, description="Mobile contact number")
    district: Optional[str] = Field(default=None, description="District")


class CitizenRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, description="Citizen's full name")
    email: str = Field(..., description="Valid email address")
    username: str = Field(..., min_length=3, description="Desired unique username")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    phone: Optional[str] = Field(default=None, description="Mobile contact number")
    district: Optional[str] = Field(default="National", description="Home district")


class AdminLoginRequest(BaseModel):
    admin_key: str = Field(..., description="Master administrator secret key or password")
    username: Optional[str] = Field(default="admin", description="Admin username")


class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    district: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    last_login: Optional[str] = None


class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[UserProfile] = None


class ForgotPasswordRequest(BaseModel):
    identifier: str = Field(..., description="Username or email address")
    role: Optional[str] = Field(default=None, description="Optional role tier: 'admin', 'officer', or 'citizen'")


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Password reset verification code / token")
    new_password: str = Field(..., min_length=6, description="New password (min 6 characters)")


# ---------------------------------------------------------------------
# AI Watershed Snip & Plan Schemas
# ---------------------------------------------------------------------
class SnipPlanRequest(BaseModel):
    north: float = Field(..., description="Northern latitude bounding coordinate")
    south: float = Field(..., description="Southern latitude bounding coordinate")
    east: float = Field(..., description="Eastern longitude bounding coordinate")
    west: float = Field(..., description="Western longitude bounding coordinate")


# ---------------------------------------------------------------------
# DEM Accumulation Simulation Schemas
# ---------------------------------------------------------------------
class SimRequest(BaseModel):
    scenario: str = Field(
        default="High",
        description="Rainfall intensity scenario: 'Moderate' (25mm), 'High' (60mm), or 'Extreme' (130mm)",
    )
    watershed_id: str = Field(
        default="WS-PERIYAR",
        description="Target watershed identifier (e.g. 'WS-PERIYAR', 'WS-BHARATHA', 'WS-PAMBA', 'WS-CHALIYAR')",
    )


# ---------------------------------------------------------------------
# Hydrological Intervention Simulation Schemas
# ---------------------------------------------------------------------
class InterventionRequest(BaseModel):
    intervention_type: str = Field(
        default="check_dams",
        description="Type of intervention: 'check_dams', 'contour_bunds', 'recharge_ponds', 'riparian_buffer', etc.",
    )
    density: int = Field(
        default=60,
        ge=0,
        le=100,
        description="Implementation density percentage (0-100%)",
    )
    watershed_id: Optional[str] = Field(
        default="WS-PERIYAR",
        description="Target watershed identifier (e.g., WS-PERIYAR, WS-BHARATHA, WS-CHALAKUDY)",
    )
    storm_event_mm: Optional[float] = Field(
        default=180.0,
        description="Design storm rainfall in mm (e.g., 100, 180, 260, 360)",
    )
    soil_type: Optional[str] = Field(
        default="laterite",
        description="Soil profile: 'laterite', 'saprolite', 'alluvium', 'loam'",
    )


# ---------------------------------------------------------------------
# Citizen & Field Report Schemas
# ---------------------------------------------------------------------
class ReportModel(BaseModel):
    district: str = Field(..., description="District name where observation occurred")
    category: str = Field(..., description="Hazard category (e.g., Landslide, Flood, Soil Erosion)")
    severity: str = Field(..., description="Severity rating: Critical, High, Moderate, or Low")
    email: Optional[str] = Field(default="operations@ksdma.kerala.gov.in", description="Submitter email address for verification contact")
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")
    desc: str = Field(..., description="Field description of incident or terrain condition")
    image: Optional[str] = Field(
        default=None,
        description="Base64 data URI or image URL demonstrating geotagged proof",
    )
    location_name: Optional[str] = Field(default=None, description="Human-readable or reverse-geocoded location name")
    reporter_role: Optional[str] = Field(default="citizen", description="Role of submitter: 'citizen', 'officer', or 'admin'")
    reporter_id: Optional[str] = Field(default=None, description="User ID of submitter")
    reporter_name: Optional[str] = Field(default=None, description="Display name of submitter")


class ReportStatusUpdate(BaseModel):
    report_id: str = Field(..., description="Unique report identifier (e.g. 'UY-REP-501')")
    status: Optional[str] = Field(
        default=None,
        description="New operational triage status ('Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved', 'Rejected', etc.)",
    )
    new_status: Optional[str] = Field(
        default=None,
        description="Alias for status",
    )
    remarks: Optional[str] = Field(default=None, description="Operational notes or resolution remarks")
    assigned_to: Optional[str] = Field(default=None, description="Responsible officer or department assignment")


class ReportDeleteRequest(BaseModel):
    report_id: str = Field(..., description="Unique report identifier to purge")


class UpvoteRequest(BaseModel):
    report_id: Optional[str] = Field(default=None, description="Unique report identifier to toggle upvote")
    user_id: Optional[str] = Field(default=None, description="User identifier")


class NotificationReadRequest(BaseModel):
    notification_id: Optional[int] = Field(default=None, description="Notification ID to mark as read")


# ---------------------------------------------------------------------
# Interactive Point Watershed Delineation Schemas (delineator)
# ---------------------------------------------------------------------
class DelineateRequest(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude of target outlet")
    lng: float = Field(..., ge=-180.0, le=180.0, description="Longitude of target outlet")
    high_res: bool = Field(
        default=False,
        description="Whether to perform sub-catchment raster splitting (requires rasters)",
    )
    rivers: bool = Field(
        default=True,
        description="Whether to extract and include upstream tributary river reaches",
    )
    snap: bool = Field(
        default=True,
        description="Whether to snap requested outlet point to nearest stream centerline",
    )
    smooth: bool = Field(
        default=True,
        description="Whether to apply Catmull-Rom spline and Chaikin boundary smoothing",
    )


class DelineateResponse(BaseModel):
    status: str
    message: Optional[str] = None
    area_km2: Optional[float] = None
    area_ha: Optional[float] = None
    requested_point: Optional[List[float]] = None
    snapped_point: Optional[List[float]] = None
    snap_distance_m: Optional[float] = None
    watershed: Optional[Dict[str, Any]] = None
    rivers: Optional[Dict[str, Any]] = None
    outlets: Optional[Dict[str, Any]] = None
    reach_count: Optional[int] = None
    megabasin: Optional[int] = None
    execution_time_ms: Optional[float] = None
    provenance: Optional[Dict[str, Any]] = None
