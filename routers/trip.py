from fastapi import APIRouter, File, Form, UploadFile

router = APIRouter(prefix="/trips", tags=["운행"])
# TODO: 2~3주차 - YOLO 카운트 모듈 / 판정 로직 연결


@router.get("/current")
def current_trip():
    """내 진행 중 운행 또는 404"""
    ...


@router.get("")
def list_trips(status: str | None = None, result: str | None = None,
               bus_id: int | None = None, limit: int = 20, offset: int = 0):
    """운행 목록과 total"""
    ...


@router.get("/{trip_id}")
def get_trip(trip_id: int):
    """운행 상세, 이벤트 목록, 열린 경고"""
    ...


@router.post("/{trip_id}/boarding-photo")
async def boarding_photo(trip_id: int, image: UploadFile = File(...),
                         captured_at: str = Form(...), exclude_count: int = Form(0)):
    """event_id, person_count, boarding_count"""
    ...


@router.post("/{trip_id}/dropoff-photo")
async def dropoff_photo(trip_id: int, image: UploadFile = File(...),
                        captured_at: str = Form(...), exclude_count: int = Form(0)):
    """event_id, remaining_count, alighted_count, result, alert_id"""
    ...


@router.post("/{trip_id}/confirm")
def confirm_trip(trip_id: int):
    """method(scan|button). status=CLOSED, result가 OK 아니면 409"""
    ...
