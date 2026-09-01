import math
import struct

from server.segmenter import SilenceSegmenter


def tone(seconds: float, freq: float = 300.0, amp: int = 6000, rate: int = 16000) -> bytes:
    n = int(seconds * rate)
    return b"".join(struct.pack("<h", int(amp * math.sin(2 * math.pi * freq * i / rate))) for i in range(n))


def silence(seconds: float, rate: int = 16000) -> bytes:
    return b"\x00\x00" * int(seconds * rate)


def feed_chunked(seg: SilenceSegmenter, data: bytes, chunk: int = 3200) -> list[bytes]:
    out = []
    for i in range(0, len(data), chunk):
        out.extend(seg.feed(data[i:i + chunk]))
    return out


def test_segment_cut_at_silence():
    seg = SilenceSegmenter(silence_s=0.5, max_segment_s=10.0)
    segments = feed_chunked(seg, tone(2.0) + silence(1.0) + tone(1.5) + silence(1.0))
    assert len(segments) == 2
    # erstes Segment: ~2s Sprache + Stille bis zum Cut
    assert len(segments[0]) >= 2.0 * 16000 * 2


def test_max_length_forces_cut():
    seg = SilenceSegmenter(silence_s=0.5, max_segment_s=3.0)
    segments = feed_chunked(seg, tone(8.0))
    assert len(segments) >= 2
    for s in segments:
        assert len(s) <= 3.1 * 16000 * 2


def test_leading_silence_dropped_and_noise_ignored():
    seg = SilenceSegmenter(silence_s=0.5, max_segment_s=10.0)
    assert feed_chunked(seg, silence(3.0)) == []
    assert seg.flush() == []


def test_flush_emits_tail():
    seg = SilenceSegmenter(silence_s=5.0, max_segment_s=60.0)
    assert feed_chunked(seg, tone(2.0)) == []
    tail = seg.flush()
    assert len(tail) == 1
