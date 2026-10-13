import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from core.security import require_admin, require_admin_header_or_query
from database.db_connection import get_db
from models.models import BoardingEvent, EventType
from services import event_bus
from services.serializers import event_to_dict, image_available

router = APIRouter(tags=["이벤트"])


def get_event_or_404(db: Session, event_id: int) -> BoardingEvent:
    e = db.get(BoardingEvent, event_id)
    if not e:
        raise HTTPException(404, "이벤트를 찾을 수 없습니다")
    return e


@router.get("/events", dependencies=[Depends(require_admin)])
def list_events(
    trip_id: int | None = None,
    event_type: EventType | None = None,
    from_: datetime | None = Query(None, alias="from"),
    to: datetime | None = None,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(BoardingEvent)
    if trip_id:
        q = q.filter(BoardingEvent.trip_id == trip_id)
    if event_type:
        q = q.filter(BoardingEvent.event_type == event_type)
    if from_:
        q = q.filter(BoardingEvent.uploaded_at >= from_)
    if to:
        q = q.filter(BoardingEvent.uploaded_at <= to)
    total = q.count()
    rows = q.order_by(BoardingEvent.id.desc()).offset(offset).limit(limit).all()
    return {"items": [event_to_dict(e) for e in rows], "total": total}


@router.get("/events/{event_id}", dependencies=[Depends(require_admin)])
def get_event(event_id: int, db: Session = Depends(get_db)):
    """이벤트 상세 + YOLO detections"""
    return event_to_dict(get_event_or_404(db, event_id), with_detections=True)


@router.get("/events/{event_id}/image", dependencies=[Depends(require_admin_header_or_query)])
def get_event_image(event_id: int, db: Session = Depends(get_db)):
    """사진 파일. 보관기간이 지났거나 파일이 없으면 410
    (<img src> 용으로 ?token=JWT 도 허용)"""
    e = get_event_or_404(db, event_id)
    if not image_available(e) or not os.path.exists(e.image_path):
        raise HTTPException(410, "보관 기간이 지나 사진이 삭제되었습니다")
    return FileResponse(e.image_path)


@router.get("/stream/events", dependencies=[Depends(require_admin_header_or_query)])
async def stream_events(request: Request):
    """SSE: 새 이벤트(event)·경고(alert) 실시간 전송.
    브라우저 EventSource 는 헤더를 못 붙이므로 ?token=JWT 도 허용"""
    return StreamingResponse(
        event_bus.sse_stream(request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
