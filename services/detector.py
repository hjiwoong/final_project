"""사람 수 카운트 (YOLO). mock ↔ real 풀백

- mock : 사진 내용을 보지 않고 지정한 수만큼 '검출'한 것처럼 반환 (개발·시연용)
- real : ultralytics YOLO(COCO) 로 person(class 0) 검출. 실패하면 mock 으로 풀백
"""
import io
import logging
import os

MODE = os.getenv("DETECTOR_MODE", "mock").lower()
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.25"))      # 이 이상만 사람으로 셈
LOW_CONF_THRESHOLD = float(os.getenv("LOW_CONF_THRESHOLD", "0.5"))  # 이 미만이면 '신뢰도 낮음'

log = logging.getLogger("detector")
_model = None


def _mock_detect(count: int, low_conf: int = 0) -> list[dict]:
    dets = []
    for i in range(count):
        is_low = i >= count - low_conf
        conf = 0.40 if is_low else round(0.95 - 0.02 * i, 2)
        dets.append({"label": "person", "conf": conf, "bbox": [10 + i * 50, 20, 60 + i * 50, 120]})
    return dets


def _real_detect(image_bytes: bytes) -> list[dict]:
    global _model
    from PIL import Image
    from ultralytics import YOLO

    if _model is None:
        _model = YOLO(YOLO_MODEL)
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    result = _model(img, classes=[0], conf=CONF_THRESHOLD, verbose=False)[0]
    dets = []
    for box in result.boxes:
        dets.append({
            "label": "person",
            "conf": round(float(box.conf[0]), 3),
            "bbox": [round(float(v), 1) for v in box.xyxy[0].tolist()],
        })
    return dets


def detect_people(
    image_bytes: bytes,
    mock_count: int | None = None,
    mock_low_conf: int = 0,
    default_count: int = 0,
) -> tuple[list[dict], str]:
    """-> (detections, 실제 사용된 모드)"""
    if MODE == "real":
        try:
            return _real_detect(image_bytes), "real"
        except Exception as e:   # noqa: BLE001
            log.warning("real 검출 실패 → mock 풀백: %s", e)
            return _mock_detect(default_count), "mock-fallback"

    count = mock_count if mock_count is not None else default_count
    return _mock_detect(count, mock_low_conf), "mock"


def low_conf_count(detections: list[dict]) -> int:
    return sum(1 for d in detections if d["conf"] < LOW_CONF_THRESHOLD)
