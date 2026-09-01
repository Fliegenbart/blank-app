"""Energie-basierte Segmentierung des Ingest-PCM-Stroms.

Schneidet den kontinuierlichen 16-kHz-Strom an Sprechpausen in Segmente,
die einzeln durch ASR/MT/TTS laufen. Kein externes VAD nötig — der Feed
vom Mischpult ist sauber (kein Raumhall, kein Publikum).
"""
from __future__ import annotations

import array
import math


class SilenceSegmenter:
    def __init__(
        self,
        sample_rate: int = 16000,
        sample_width: int = 2,
        silence_s: float = 0.6,
        max_segment_s: float = 7.0,
        min_segment_s: float = 1.0,
        frame_ms: int = 30,
        threshold: int = 300,
    ) -> None:
        self.sample_rate = sample_rate
        self.sample_width = sample_width
        self.frame_bytes = int(sample_rate * frame_ms / 1000) * sample_width
        self.silence_frames = max(1, int(silence_s * 1000 / frame_ms))
        self.max_frames = max(1, int(max_segment_s * 1000 / frame_ms))
        self.min_frames = max(1, int(min_segment_s * 1000 / frame_ms))
        self.threshold = threshold

        self._pending = b""
        self._frames: list[bytes] = []
        self._voiced = 0
        self._trailing_silence = 0

    def _frame_is_voiced(self, frame: bytes) -> bool:
        samples = array.array("h")
        samples.frombytes(frame)
        if not samples:
            return False
        rms = math.sqrt(sum(s * s for s in samples) / len(samples))
        return rms >= self.threshold

    def feed(self, data: bytes) -> list[bytes]:
        """Nimmt beliebig große PCM-Häppchen entgegen, liefert fertige Segmente."""
        out: list[bytes] = []
        self._pending += data
        while len(self._pending) >= self.frame_bytes:
            frame = self._pending[: self.frame_bytes]
            self._pending = self._pending[self.frame_bytes:]
            out.extend(self._push_frame(frame))
        return out

    def _push_frame(self, frame: bytes) -> list[bytes]:
        voiced = self._frame_is_voiced(frame)
        if not self._frames and not voiced:
            return []  # Stille vor Sprechbeginn verwerfen
        self._frames.append(frame)
        if voiced:
            self._voiced += 1
            self._trailing_silence = 0
        else:
            self._trailing_silence += 1

        end_by_silence = self._trailing_silence >= self.silence_frames and len(self._frames) >= self.min_frames
        end_by_length = len(self._frames) >= self.max_frames
        if end_by_silence or end_by_length:
            return self._emit()
        return []

    def _emit(self) -> list[bytes]:
        segment = b"".join(self._frames)
        voiced = self._voiced
        self._frames = []
        self._voiced = 0
        self._trailing_silence = 0
        if voiced < self.min_frames // 3:
            return []  # praktisch nur Stille/Rauschen
        return [segment]

    def flush(self) -> list[bytes]:
        """Beim Stream-Ende Rest ausgeben."""
        if not self._frames:
            return []
        return self._emit()
