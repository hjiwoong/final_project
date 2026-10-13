from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.security import require_admin
from database.db_connection import get_db
from database.orm import init_db
from services.detector import MODE as DETECTOR_MODE
from routers import (
    alert, boarding_event, bus, bus_student, guardian,
    notification, stats, student, trip, user,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()   # 서버 시작 시 MySQL 에 테이블 생성
    yield


app = FastAPI(title="AI 통학버스 미하차 교차검증·안전관리", lifespan=lifespan)

# 관리자 웹(브라우저)에서 호출할 수 있도록 CORS 허용 (개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(bus.router, dependencies=[Depends(require_admin)])
app.include_router(student.router)
app.include_router(bus_student.router, dependencies=[Depends(require_admin)])
app.include_router(guardian.router, dependencies=[Depends(require_admin)])
app.include_router(trip.router)
app.include_router(boarding_event.router)
app.include_router(alert.router)
app.include_router(notification.router)
app.include_router(stats.router)


@app.get("/health", tags=["시스템"])
def health(db: Session = Depends(get_db)):
    """서버·DB 상태, detector_mode"""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected", "detector_mode": DETECTOR_MODE}
