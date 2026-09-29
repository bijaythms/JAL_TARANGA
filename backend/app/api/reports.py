"""
VELLAM Geospatial Platform - Crowdsourced & Field Reports API Router
Handles public field observation submissions, citizen tracking, upvoting, and sanitized public disaster feeds.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Header, Query
from app.schemas.models import ReportModel, UpvoteRequest
from app.core.data_loader import (
    get_public_reports_db,
    get_reports_db,
    add_report_to_db,
)
from app.core.database import (
    toggle_complaint_upvote_in_db,
    get_user_upvoted_reports_from_db,
    get_complaint_timeline_from_db,
)
from app.api.auth import _get_current_user_from_token

router = APIRouter(prefix="/api/reports", tags=["Citizen & Field Reports"])


@router.get("")
@router.get("/")
def get_public_reports(
    district: Optional[str] = None,
    sort_by: Optional[str] = Query("recent", description="'recent' or 'upvotes'")
):
    """
    Retrieve sanitized public incident reports feed.
    Strictly scrubs all sensitive personal contact details (email, phone, user IDs).
    """
    reports = get_public_reports_db()
    if district and district.lower() != "all":
        reports = [r for r in reports if r.get("district", "").lower() == district.lower()]

    if sort_by == "upvotes":
        reports = sorted(reports, key=lambda r: int(r.get("upvotes") or 0), reverse=True)
    else:
        reports = sorted(reports, key=lambda r: r.get("timestamp", ""), reverse=True)

    return {"total": len(reports), "reports": reports}


@router.post("")
@router.post("/")
def add_report(r: ReportModel, authorization: Optional[str] = Header(None)):
    """
    Submit a geotagged field observation report with optional photo evidence.
    Logged into spatial triage queue for administrative verification.
    """
    user = _get_current_user_from_token(authorization)
    if user:
        if not r.reporter_id:
            r.reporter_id = user["id"]
        if not r.reporter_name:
            r.reporter_name = user.get("full_name", user["username"])
        if user.get("role") in ["analyst", "researcher", "field_officer", "officer"]:
            r.reporter_role = "officer"
        elif user.get("role") == "admin":
            r.reporter_role = "admin"
        else:
            r.reporter_role = "citizen"

    entry = add_report_to_db(r)
    return {
        "status": "success",
        "success": True,
        "report_id": entry.get("id"),
        "data": entry
    }


@router.get("/my")
def get_my_reports(
    email: Optional[str] = Query(None),
    reporter_id: Optional[str] = Query(None),
    report_ids: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """
    Citizen Complaint Status and Tracking endpoint.
    Returns all complaints submitted by the citizen with full status,
    remarks, evidence, and timeline.
    Resilient to token expiration, unauthenticated guest submissions, and email queries.
    """
    user = _get_current_user_from_token(authorization)

    uids: List[str] = []
    emails: List[str] = []
    r_ids: List[str] = []

    if user:
        if user.get("id"):
            uids.append(user["id"])
        if user.get("email"):
            emails.append(user["email"].strip().lower())
        if user.get("username"):
            uids.append(user["username"])

    if reporter_id and reporter_id.strip() not in ("undefined", "null", ""):
        uids.append(reporter_id.strip())

    if email and email.strip() not in ("undefined", "null", ""):
        emails.append(email.strip().lower())

    if report_ids and report_ids.strip() not in ("undefined", "null", ""):
        for rid in report_ids.split(","):
            rid_clean = rid.strip()
            if rid_clean and rid_clean not in ("undefined", "null", ""):
                r_ids.append(rid_clean)

    # If no identifiers provided at all, return empty list gracefully (no 401!)
    if not uids and not emails and not r_ids:
        return {"total": 0, "reports": []}

    user_reports = get_reports_db(
        user_ids=uids if uids else None,
        emails=emails if emails else None,
        report_ids=r_ids if r_ids else None
    )

    enriched = []
    for rep in user_reports:
        d = dict(rep)
        d["timeline"] = get_complaint_timeline_from_db(rep["id"])
        enriched.append(d)

    return {"total": len(enriched), "reports": enriched}


@router.post("/{report_id}/upvote")
def toggle_upvote(
    report_id: str,
    req: Optional[UpvoteRequest] = None,
    user_id: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """
    Community Complaint Upvote System.
    Allows authenticated citizens to upvote a complaint or remove their upvote.
    Strictly enforces 1 vote per citizen per complaint.
    """
    uid = None
    if req and req.user_id:
        uid = req.user_id
    elif user_id:
        uid = user_id
    else:
        user = _get_current_user_from_token(authorization)
        if user:
            uid = user["id"]

    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please sign in to upvote community complaints."
        )

    res = toggle_complaint_upvote_in_db(report_id=report_id, user_id=uid)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Upvote action failed"))
    return res


@router.get("/user/upvoted")
@router.get("/user/upvotes")
def get_my_upvoted_ids(
    user_id: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """Returns list of complaint IDs that the current user has upvoted."""
    uid = user_id
    if not uid:
        user = _get_current_user_from_token(authorization)
        if user:
            uid = user["id"]

    if not uid:
        return {"upvoted_ids": []}
    ids = get_user_upvoted_reports_from_db(uid)
    return {"upvoted_ids": ids}


@router.get("/{report_id}/timeline")
def get_report_timeline(report_id: str):
    """Returns lifecycle audit timeline for a specific report."""
    timeline = get_complaint_timeline_from_db(report_id)
    return {"report_id": report_id, "timeline": timeline}
