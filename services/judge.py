"""미하차 판정 로직 (수 비교)

하차 수 = 승차 수 - 종점 잔류 수
잔류 1명 이상            -> MISSED      (긴급)
잔류 0 이지만 신뢰도 낮음 -> NEEDS_CHECK (확인 필요)
그 외                    -> OK
"""
from models.models import AlertLevel, TripResult


def judge(boarding_count: int, remaining_count: int, low_conf: int) -> dict:
    alighted = max(boarding_count - remaining_count, 0)

    if remaining_count >= 1:
        result, level = TripResult.MISSED, AlertLevel.URGENT
        message = f"미하차 의심 {remaining_count}명"
    elif low_conf >= 1:
        result, level = TripResult.NEEDS_CHECK, AlertLevel.CHECK
        message = f"확인 필요 (신뢰도 낮은 검출 {low_conf}건)"
    else:
        result, level, message = TripResult.OK, None, "하차 확인 완료"

    return {
        "result": result,
        "level": level,
        "message": message,
        "alighted_count": alighted,
    }
