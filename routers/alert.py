from fastapi import APIRouter

router = APIRouter(tags=["경고"])


@router.get("/alerts")
def list_alerts(status: str | None = None, level: str | None = None,
                limit: int = 20, offset: int = 0):
    """경고 목록과 total"""
    ...


@router.get("/alerts/{alert_id}")
def get_alert(alert_id: int):
    """경고 상세, llm_summary, 연결된 이벤트"""
    ...


@router.post("/alerts/{alert_id}/ack")
def ack_alert(alert_id: int):
    """status=ACKED"""
    ...


@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int):
    """note -> status=RESOLVED"""
    ...


@router.get("/me/alerts")
def my_alerts(status: str | None = None, limit: int = 20, offset: int = 0):
    """학부모: 내 아이가 탄 버스의 경고 목록"""
    ...
