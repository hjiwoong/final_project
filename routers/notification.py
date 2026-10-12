from fastapi import APIRouter

router = APIRouter(prefix="/me/notifications", tags=["학부모-알림"])


@router.get("")
def my_notifications(unread_only: bool = False, limit: int = 20, offset: int = 0):
    """알림 목록"""
    ...


@router.post("/{notification_id}/read")
def read_notification(notification_id: int):
    """읽음 처리 -> read_at"""
    ...
