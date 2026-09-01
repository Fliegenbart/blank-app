"""Deutsche Sprachausgabe.

- PiperTTS: piper-Binary (schnell, CPU, Stimme z. B. de_DE-thorsten-high),
  Ausgabe-WAV wird per ffmpeg nach MP3 (64 kbit/s mono) kodiert — MP3 dekodiert
  jeder Smartphone-Browser (inkl. iOS Safari) via decodeAudioData.
- FakeTTS: kurzer Sinuston für Tests ohne Modelle.
"""
from __future__ import annotations

import io
import logging
import math
import struct
import subprocess
import wave

log = logging.getLogger("nex26.tts")


def wav_to_mp3(wav_bytes: bytes) -> bytes:
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error",
         "-f", "wav", "-i", "pipe:0",
         "-ac", "1", "-b:a", "64k", "-f", "mp3", "pipe:1"],
        input=wav_bytes, capture_output=True, check=True,
    )
    return proc.stdout


class FakeTTS:
    def synthesize(self, text: str) -> bytes:
        """0,3 s 440-Hz-Ton als MP3 — nur für NEX26_FAKE_PIPELINE."""
        rate = 22050
        n = int(rate * 0.3)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            frames = b"".join(
                struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / rate)))
                for i in range(n)
            )
            w.writeframes(frames)
        try:
            return wav_to_mp3(buf.getvalue())
        except (FileNotFoundError, subprocess.CalledProcessError):
            return buf.getvalue()  # ffmpeg fehlt im Test-Env: WAV geht auch


class PiperTTS:
    def __init__(self, voice: str, piper_bin: str = "piper") -> None:
        self.voice = voice
        self.piper_bin = piper_bin

    def synthesize(self, text: str) -> bytes:
        proc = subprocess.run(
            [self.piper_bin, "--model", self.voice, "--output-raw"],
            input=text.encode("utf-8"), capture_output=True, check=True,
        )
        raw = proc.stdout  # 22050 Hz s16le mono
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(22050)
            w.writeframes(raw)
        return wav_to_mp3(buf.getvalue())
