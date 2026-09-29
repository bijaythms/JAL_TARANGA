"""
VELLAM Geospatial Platform - Admin API Router
Handles administrative authentication, incident report moderation, and queue management.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Header
from app.schemas.models import AdminAuthRequest, ReportStatusUpdate, ReportDeleteRequest
from app.core.security import verify_admin_key
from app.core.data_loader import get_reports_db, update_report_in_db, delete_report_from_db

router = APIRouter(prefix="/api/admin", tags=["Admin Operations"])


@router.post("/verify")
def verify_key(req: AdminAuthRequest):
    """
    Secure server-side validation of secret key for administrative access.
    Key comparison is timing-attack resistant.
    """
    if verify_admin_key(req.key):
        return {"authenticated": True, "message": "Access Granted"}
    return {"authenticated": False, "message": "Invalid Key"}


@router.get("/reports")
def get_admin_reports(reporter_role: Optional[str] = None):
    """
    Retrieve all disaster and watershed reports with full metadata,
    including submitter emails, reporter role (citizen vs officer),
    location names, and remarks.
    """
    role_filter = None if not reporter_role or reporter_role.lower() == "all" else reporter_role.lower()
    reports = get_reports_db(reporter_role=role_filter)
    return {"total": len(reports), "reports": reports}


@router.post("/update-status")
def update_status(update: ReportStatusUpdate, authorization: Optional[str] = Header(None)):
    """
    Update the operational workflow status of a field report.
    (e.g., 'Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved', 'Rejected')
    Records remarks, responsible officer assignment, and creates timeline audit trail.
    """
    from app.api.auth import _get_current_user_from_token
    user = _get_current_user_from_token(authorization)
    updated_by = user.get("full_name", user["username"]) if user else "State Emergency Admin"
    updated_by_role = user.get("role", "admin") if user else "admin"

    target_status = update.status or update.new_status or "Under Review"
    updated_report = update_report_in_db(
        report_id=update.report_id,
        new_status=target_status,
        remarks=update.remarks,
        assigned_to=update.assigned_to,
        updated_by=updated_by,
        updated_by_role=updated_by_role
    )
    if updated_report:
        return {"status": "success", "success": True, "updated": updated_report}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")


@router.post("/delete-report")
def delete_report(req: ReportDeleteRequest):
    """
    Purge a report from the system (for invalid or duplicate submissions).
    """
    deleted = delete_report_from_db(req.report_id)
    if deleted:
        return {"status": "success", "deleted_id": req.report_id}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")


@router.get("/users")
def get_admin_users():
    """
    Retrieve all registered users from PostgreSQL vellam_db across Citizens, Officers, and Admins.
    """
    from app.core.user_store import load_citizens, load_officers, load_admins, get_database_stats
    citizens = load_citizens()
    officers = load_officers()
    admins = load_admins()

    def _clean_user(u: dict, tier: str) -> dict:
        return {
            "id": u.get("id"),
            "username": u.get("username"),
            "email": u.get("email"),
            "full_name": u.get("full_name"),
            "phone": u.get("phone", "—"),
            "district": u.get("district", "—"),
            "role": u.get("role"),
            "designation": u.get("designation", "—"),
            "department": u.get("department", "—"),
            "tier": tier,
            "is_active": u.get("is_active", True),
            "created_at": u.get("created_at"),
            "last_login": u.get("last_login"),
        }

    all_users = (
        [_clean_user(u, "Citizen") for u in citizens] +
        [_clean_user(u, "Officer") for u in officers] +
        [_clean_user(u, "Administrator") for u in admins]
    )

    return {
        "status": "success",
        "total": len(all_users),
        "users": all_users,
        "counts": {
            "citizens": len(citizens),
            "officers": len(officers),
            "admins": len(admins),
        },
        "stats": get_database_stats()
    }

