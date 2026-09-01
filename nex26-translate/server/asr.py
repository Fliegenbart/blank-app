"""ASR-Backends: faster-whisper (echt) und Stub (Tests)."""
from __future__ import annotations

import logging

log = logging.getLogger("nex26.asr")


class FakeASR:
    def transcribe(self, pcm: bytes) -> str:
        seconds = len(pcm) / 32000
        return f"[fake transcript, {seconds:.1f}s of audio]"


class WhisperASR:
    def __init__(self, model_name: str, device: str, initial_prompt: str = "") -> None:
        from faster_whisper import WhisperModel  # lazy: schwere Abhängigkeit

        compute = "float16" if device in ("cuda", "auto") else "int8"
        log.info("Loading faster-whisper model %s on %s (%s)", model_name, device, compute)
        try:
            self.model = WhisperModel(model_name, device=device, compute_type=compute)
        except (ValueError, RuntimeError):
            log.warning("Falling back to CPU/int8")
            self.model = WhisperModel(model_name, device="cpu", compute_type="int8")
        self.initial_prompt = initial_prompt or None

    def transcribe(self, pcm: bytes) -> str:
        import numpy as np

        audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
        segments, _info = self.model.transcribe(
            audio,
            language="en",
            beam_size=2,
            condition_on_previous_text=False,
            initial_prompt=self.initial_prompt,
            vad_filter=True,
        )
        return " ".join(s.text.strip() for s in segments).strip()
