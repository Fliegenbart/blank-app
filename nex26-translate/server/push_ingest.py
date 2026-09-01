"""ffmpeg-stdin -> WebSocket-Ingest-Brücke.

Nutzung (Laptop am FoH-Platz, Audio-Interface am Mischpult-Ausgang):

    ffmpeg -f alsa -i hw:1 -ac 1 -ar 16000 -f s16le - \
      | python -m server.push_ingest wss://HOST/ws/ingest?token=TOKEN
"""
from __future__ import annotations

import asyncio
import sys

import websockets

CHUNK = 3200  # 100 ms bei 16 kHz s16le mono


async def run(url: str) -> None:
    async with websockets.connect(url, max_size=None) as ws:
        loop = asyncio.get_running_loop()
        while True:
            data = await loop.run_in_executor(None, sys.stdin.buffer.read, CHUNK)
            if not data:
                break
            await ws.send(data)


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    asyncio.run(run(sys.argv[1]))


if __name__ == "__main__":
    main()
