"""
VELLAM Geospatial Platform - Persistent Notifications API Router
Provides endpoints for retrieving unread alerts, marking notifications as read,
and dispatching operational notices to citizens and administrators.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Header
from app.api.auth import _get_current_user_from_token
from app.core.database import (
    get_user_notifications_from_db,
    mark_notification_read_in_db,
    create_notification_in_db,
)

router = APIRouter(prefix="/api/notifications", tags=["Notification Engine"])


@router.get("")
@router.get("/")
def get_notifications(
    user_id: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    """
    Retrieves persistent notifications for the active user session.
    Admins and officers receive targeted alerts as well as system-wide dispatch bulletins.
    """
    uid = user_id
    is_staff = False
    if authorization:
        user = _get_current_user_from_token(authorization)
        if user:
            uid = user["id"]
            is_staff = user.get("role") in ["admin", "analyst", "researcher", "field_officer", "officer"]

    if not uid:
        return {"unread_count": 0, "notifications": []}

    data = get_user_notifications_from_db(user_id=uid, is_admin=is_staff)
    return data


@router.post("/{notification_id}/read")
def mark_single_read(notification_id: int, authorization: Optional[str] = Header(None)):
    """
    Marks a single notification as read.
    """
    user = _get_current_user_from_token(authorization)
    user_id = user["id"] if user else "anonymous"
    success = mark_notification_read_in_db(notif_id=notification_id, user_id=user_id)
    return {"success": success, "notification_id": notification_id}


@router.post("/read-all")
def mark_all_read(authorization: Optional[str] = Header(None)):
    """
    Marks all notifications for the active user as read.
    """
    user = _get_current_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    success = mark_notification_read_in_db(notif_id=None, user_id=user["id"])
    return {"success": success, "message": "All notifications marked as read"}

