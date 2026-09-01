from __future__ import annotations

import hmac
import io
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, Response

from .broadcast import Broadcaster
from .config import settings
from .pipeline import Pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("nex26")

STATIC = Path(__file__).resolve().parent.parent / "static"

broadcaster = Broadcaster()
pipeline: Pipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline
    if not settings.ingest_token and not settings.fake_pipeline:
        raise RuntimeError("NEX26_INGEST_TOKEN muss gesetzt sein")
    pipeline = Pipeline(settings, broadcaster)
    await pipeline.start()
    log.info("Pipeline ready (fake=%s)", settings.fake_pipeline)
    yield
    await pipeline.stop()


app = FastAPI(title="NeX26 Live Translation", lifespan=lifespan)


def _token_ok(token: str) -> bool:
    expected = settings.ingest_token or ("dev" if settings.fake_pipeline else "")
    return bool(expected) and hmac.compare_digest(token, expected)


@app.get("/", response_class=HTMLResponse)
async def listener_page():
    return FileResponse(STATIC / "listener.html")


@app.get("/stage", response_class=HTMLResponse)
async def stage_page(token: str = Query(default="")):
    if not _token_ok(token):
        raise HTTPException(403, "Token fehlt oder falsch (?token=...)")
    return FileResponse(STATIC / "stage.html")


@app.get("/health")
async def health():
    return {"status": "ok", **(pipeline.stats() if pipeline else {})}


@app.get("/qr")
async def qr_code():
    import qrcode

    img = qrcode.make(settings.public_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(buf.getvalue(), media_type="image/png")


@app.websocket("/ws/ingest")
async def ws_ingest(ws: WebSocket, token: str = Query(default="")):
    if not _token_ok(token):
        await ws.close(code=4403)
        return
    await ws.accept()
    assert pipeline is not None
    segmenter = pipeline.new_segmenter()
    log.info("Ingest connected")
    try:
        while True:
            data = await ws.receive_bytes()
            for segment in segmenter.feed(data):
                await pipeline.submit(segment)
    except WebSocketDisconnect:
        for segment in segmenter.flush():
            await pipeline.submit(segment)
        log.info("Ingest disconnected")


@app.websocket("/ws/listen")
async def ws_listen(ws: WebSocket):
    await ws.accept()
    await broadcaster.register(ws)
    try:
        while True:
            # Hörer senden nichts Relevantes; Empfang hält die Verbindung offen
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await broadcaster.unregister(ws)
