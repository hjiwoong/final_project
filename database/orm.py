from sqlalchemy.orm import DeclarativeBase

from database.db_connection import engine


class Base(DeclarativeBase):
    pass


def init_db():
    """models 를 import 해서 테이블을 MySQL 에 생성 (이미 있으면 건너뜀)"""
    import models.models  # noqa: F401  (테이블 등록용)

    Base.metadata.create_all(bind=engine)
