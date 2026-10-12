from fastapi import APIRouter

router = APIRouter(tags=["이벤트"])


@router.get("/events")
def list_events(trip_id: int | None = None, event_type: str | None = None,
                limit: int = 20, offset: int = 0):
    """BoardingEvent 목록과 total"""
    ...


@router.get("/events/{event_id}")
def get_event(event_id: int):
    """이벤트 상세, detections"""
    ...


@router.get("/events/{event_id}/image")
def get_event_image(event_id: int):
    """사진 파일. 보관기간 지났으면 410"""
    ...


@router.get("/stream/events")
async def stream_events():
    """SSE로 새 이벤트·경고 실시간 전송"""
    ...
