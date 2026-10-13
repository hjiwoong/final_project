"""SSE 실시간 이벤트 버스 (서버 메모리, 단일 프로세스용)

publish("alert", {...}) 를 호출하면 연결된 모든 SSE 클라이언트에게 전달된다.
동기(스레드) 코드와 async 코드 어디서든 호출할 수 있다.
"""
import asyncio
import json
from dataclasses import dataclass


@dataclass(eq=False)
class _Subscriber:
    loop: asyncio.AbstractEventLoop
    queue: asyncio.Queue


_subscribers: set[_Subscriber] = set()


def _put(q: asyncio.Queue, msg: str) -> None:
    try:
        q.put_nowait(msg)
    except asyncio.QueueFull:
        pass   # 느린 클라이언트는 메시지를 건너뜀


def format_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str, ensure_ascii=False)}\n\n"


def publish(event: str, data: dict) -> None:
    msg = format_sse(event, data)
    for sub in list(_subscribers):
        try:
            sub.loop.call_soon_threadsafe(_put, sub.queue, msg)
        except RuntimeError:        # 이벤트 루프가 이미 닫힘
            _subscribers.discard(sub)


async def sse_stream(request, keepalive_sec: float = 15.0):
    """StreamingResponse 에 넘길 async generator"""
    sub = _Subscriber(asyncio.get_running_loop(), asyncio.Queue(maxsize=200))
    _subscribers.add(sub)
    try:
        yield format_sse("connected", {"ok": True})
        while True:
            if await request.is_disconnected():
                break
            try:
                yield await asyncio.wait_for(sub.queue.get(), timeout=keepalive_sec)
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"     # 프록시/브라우저 연결 유지용
    finally:
        _subscribers.discard(sub)
