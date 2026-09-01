"""Orchestrierung: PCM-Segmente -> ASR -> MT -> TTS -> Broadcast.

Blocking-Inferenz läuft in Threads (asyncio.to_thread), damit Ingest- und
Hörer-WebSockets flüssig bleiben. Ein Worker verarbeitet Segmente seriell —
das erhält die Reihenfolge von Untertiteln und Audio.
"""
from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path

from .asr import FakeASR, WhisperASR
from .broadcast import Broadcaster
from .config import Settings
from .glossary import Glossary
from .segmenter import SilenceSegmenter
from .translate import FakeTranslator, build_translator
from .tts import FakeTTS, PiperTTS

log = logging.getLogger("nex26.pipeline")


class Pipeline:
    def __init__(self, settings: Settings, broadcaster: Broadcaster) -> None:
        self.settings = settings
        self.broadcaster = broadcaster
        self.glossary = Glossary.load(settings.glossary_path)
        self.queue: asyncio.Queue[tuple[bytes, float]] = asyncio.Queue(maxsize=32)
        self.segments_in = 0
        self.segments_done = 0
        self.last_latency_s = 0.0
        self._worker_task: asyncio.Task | None = None
        self._log_file = None

        if settings.fake_pipeline:
            self.asr = FakeASR()
            self.mt = FakeTranslator()
            self.tts = FakeTTS()
        else:
            self.asr = WhisperASR(settings.whisper_model, settings.device,
                                  initial_prompt=self.glossary.whisper_prompt())
            self.mt = build_translator(settings.translator, settings.deepl_api_key, self.glossary)
            self.tts = PiperTTS(settings.piper_voice, settings.piper_bin)

        if settings.record:
            settings.log_dir.mkdir(parents=True, exist_ok=True)
            path = Path(settings.log_dir) / f"transcript-{int(time.time())}.tsv"
            self._log_file = path.open("a", encoding="utf-8")

    def new_segmenter(self) -> SilenceSegmenter:
        return SilenceSegmenter(
            sample_rate=self.settings.sample_rate,
            sample_width=self.settings.sample_width,
            silence_s=self.settings.silence_s,
            max_segment_s=self.settings.max_segment_s,
        )

    async def start(self) -> None:
        self._worker_task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        if self._worker_task:
            self._worker_task.cancel()
        if self._log_file:
            self._log_file.close()

    async def submit(self, pcm_segment: bytes) -> None:
        self.segments_in += 1
        try:
            self.queue.put_nowait((pcm_segment, time.monotonic()))
        except asyncio.QueueFull:
            # Überlast: ältestes Segment verwerfen statt Latenz aufzubauen
            log.warning("Pipeline overloaded, dropping oldest segment")
            try:
                self.queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            self.queue.put_nowait((pcm_segment, time.monotonic()))

    async def _worker(self) -> None:
        while True:
            pcm, t0 = await self.queue.get()
            try:
                await self._process(pcm, t0)
            except Exception:
                log.exception("Segment processing failed")

    async def _process(self, pcm: bytes, t0: float) -> None:
        text_en = await asyncio.to_thread(self.asr.transcribe, pcm)
        if not text_en.strip():
            return
        text_de = await asyncio.to_thread(self.mt.translate, text_en)
        mp3 = b""
        if text_de.strip():
            try:
                mp3 = await asyncio.to_thread(self.tts.synthesize, text_de)
            except Exception:
                log.exception("TTS failed, sending captions only")
        latency = time.monotonic() - t0
        self.last_latency_s = latency
        self.segments_done += 1
        if self._log_file:
            self._log_file.write(f"{time.time():.0f}\t{text_en}\t{text_de}\n")
            self._log_file.flush()
        await self.broadcaster.push_segment(text_en, text_de, mp3, latency)

    def stats(self) -> dict:
        return {
            "segments_in": self.segments_in,
            "segments_done": self.segments_done,
            "queue_depth": self.queue.qsize(),
            "last_latency_s": round(self.last_latency_s, 2),
            "listeners": self.broadcaster.listener_count,
            "fake": self.settings.fake_pipeline,
        }
