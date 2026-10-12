from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.db_connection import get_db
from models.models import Attendance, Student

router = APIRouter(tags=["관리-학생"])


class StudentCreate(BaseModel):
    name: str
    class_name: str | None = None
    consent_at: datetime | None = None


class AttendanceSet(BaseModel):
    date: date
    is_absent: bool


def student_to_dict(s: Student) -> dict:
    return {
        "id": s.id, "name": s.name, "class_name": s.class_name,
        "consent_at": s.consent_at,
    }


@router.post("/admin/students", status_code=201)
def create_student(body: StudentCreate, db: Session = Depends(get_db)):
    s = Student(**body.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return student_to_dict(s)


@router.get("/admin/students")
def list_students(db: Session = Depends(get_db)):
    return [student_to_dict(s) for s in db.query(Student).all()]


@router.put("/students/{student_id}/attendance")
def set_attendance(student_id: int, body: AttendanceSet, db: Session = Depends(get_db)):
    """학부모 앱: 자녀 출석/결석 설정 (TODO: 내 자녀인지 JWT로 검증)"""
    if not db.get(Student, student_id):
        raise HTTPException(404, "학생을 찾을 수 없습니다")
    a = (
        db.query(Attendance)
        .filter(Attendance.student_id == student_id, Attendance.date == body.date)
        .first()
    )
    if a:
        a.is_absent = body.is_absent
    else:
        a = Attendance(student_id=student_id, date=body.date, is_absent=body.is_absent)
        db.add(a)
    db.commit()
    return {"student_id": student_id, "date": body.date, "is_absent": body.is_absent}
