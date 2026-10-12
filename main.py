from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.db_connection import get_db
from database.orm import init_db
from routers import (
    alert, boarding_event, bus, bus_student, guardian,
    notification, student, trip, user,
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
app.include_router(bus.router)
app.include_router(student.router)
app.include_router(bus_student.router)
app.include_router(guardian.router)
app.include_router(trip.router)
app.include_router(boarding_event.router)
app.include_router(alert.router)
app.include_router(notification.router)


@app.get("/health", tags=["시스템"])
def health(db: Session = Depends(get_db)):
    """서버·DB 상태, detector_mode"""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected", "detector_mode": "mock"}

if __name__ == "__main__": #직접 실행 시 uvicorn 서버 시작, python main.py 로 실행할 때만 동작
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)