"""Hub, der Untertitel (JSON) und Audio-Segmente (binär MP3) an alle Hörer verteilt."""
from __future__ import annotations

import asyncio
import json
import logging
import time

from starlette.websockets import WebSocket

log = logging.getLogger("nex26.broadcast")


class Broadcaster:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._lock = asyncio.Lock()
        self.segments_sent = 0
        self.last_caption: dict | None = None

    @property
    def listener_count(self) -> int:
        return len(self._clients)

    async def register(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.add(ws)
        if self.last_caption:
            try:
                await ws.send_text(json.dumps(self.last_caption))
            except Exception:
                pass

    async def unregister(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(ws)

    async def _send_all(self, send_coro_name: str, payload) -> None:
        async with self._lock:
            clients = list(self._clients)
        dead: list[WebSocket] = []
        for ws in clients:
            try:
                await getattr(ws, send_coro_name)(payload)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    self._clients.discard(ws)

    async def push_segment(self, text_en: str, text_de: str, mp3: bytes, latency_s: float) -> None:
        caption = {
            "type": "caption",
            "en": text_en,
            "de": text_de,
            "ts": time.time(),
            "latency_s": round(latency_s, 2),
        }
        self.last_caption = caption
        await self._send_all("send_text", json.dumps(caption))
        if mp3:
            await self._send_all("send_bytes", mp3)
        self.segments_sent += 1
