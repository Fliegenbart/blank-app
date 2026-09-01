# NeX26 Live Translation

Selbstgehostete Live-Übersetzung (Englisch → Deutsch) für die E.ON New Energy Experience 2026,
16.09.2026, Elbphilharmonie Hamburg. Alternative zu Wordly / klassischer Simultanverdolmetschung.

**Pipeline:** Bühnen-Audio → faster-whisper (ASR, EN) → Übersetzung (DeepL API oder lokales Opus-MT) → Piper TTS (DE) → WebSocket-Broadcast → Smartphone-Browser der Gäste (QR-Code, keine App-Installation).

Zusätzlich zu Audio werden **deutsche Live-Untertitel** an alle Clients gesendet.

## Architektur

```
Mischpult (Clean Feed, EN)
        │  (Laptop am FoH: stage.html erfasst Audio-Interface via Browser,
        │   oder ffmpeg-Kommando, siehe unten)
        ▼  WebSocket /ws/ingest (16 kHz PCM, geschützt per Token)
┌─────────────────────────── Hetzner-Server ───────────────────────────┐
│ Segmenter (Stille-Erkennung, Chunks 1–8 s)                           │
│   → ASR: faster-whisper (EN-Transkript)                              │
│   → MT:  DeepL API  oder  Helsinki-NLP opus-mt-en-de (lokal)         │
│   → TTS: Piper (de_DE-thorsten-high), WAV → MP3 (ffmpeg, 64 kbit/s)  │
│   → Broadcaster                                                      │
└──────────────────────────────────────────────────────────────────────┘
        ▼  WebSocket /ws/listen (JSON-Untertitel + MP3-Segmente)
  ~200 Hörer:innen im Browser (listener.html), Web-Audio-Playback
```

Latenz Bühne→Ohr: typisch **3–8 Sekunden** (Segmentlänge + ASR + MT + TTS).
Bandbreite Server→Publikum: 64 kbit/s MP3 × 200 Clients ≈ **13 Mbit/s** in Spitzen — unkritisch.

## Endpunkte

| Pfad | Zweck |
|---|---|
| `/` | Hörer-Seite (Audio + Untertitel), für QR-Code |
| `/stage` | Regie-Seite: Audio-Aufnahme vom Interface, Pegel, Status (Token nötig) |
| `/qr` | QR-Code für die Hörer-URL (Ausdruck Garderobe/Foyer) |
| `/health` | Status + Pipeline-Statistiken (JSON) |
| `/ws/ingest?token=…` | Audio-Eingang (binär, 16 kHz mono s16le PCM) |
| `/ws/listen` | Broadcast an Hörer |

## Betrieb

### Server-Dimensionierung (Hetzner)

- **Empfohlen: GPU-Server** (z. B. GEX44, RTX 4000 SFF Ada, ~€200/Monat) → faster-whisper
  `large-v3` in Echtzeit, beste Qualität. Für ein Einzel-Event 1 Monat mieten.
- **CPU-only** (z. B. AX52): Modell `small`/`distil-medium.en` — funktioniert, spürbar
  schlechtere ASR-Qualität bei Fachvokabular. Nur als Sparvariante.
- 200 WebSocket-Clients sind für einen einzelnen uvicorn-Prozess problemlos.

### Installation (Docker)

```bash
cp .env.example .env    # Token + DeepL-Key eintragen
docker compose up -d --build
```

TLS ist Pflicht (getUserMedia + iPhone): Reverse-Proxy davor, z. B. Caddy:

```
nex26.example.com {
    reverse_proxy 127.0.0.1:8026
}
```

### Audio-Zuspielung ohne Browser (Alternative zu /stage)

```bash
ffmpeg -f alsa -i hw:1 -ac 1 -ar 16000 -f s16le - \
  | python -m server.push_ingest wss://nex26.example.com/ws/ingest?token=TOKEN
```

### Glossar

E.ON-/Energie-Fachbegriffe, Namen, Produktnamen in `glossary.csv` pflegen
(`en,de` pro Zeile). Wird bei DeepL als Glossar angelegt, bei lokaler MT als
erzwungene Ersetzung nachgelagert angewendet; zusätzlich als `initial_prompt`
an Whisper gegeben (verbessert Erkennung von Eigennamen).

### Fallback-Konzept

1. **Zweiter Server** (Failover-DNS oder zweite URL auf dem QR-Aushang).
2. Pipeline läuft komplett auf dem eigenen Server — fällt nur die Hallen-Internetanbindung
   aus, hilft eine LTE/5G-Bonding-Lösung für den Ingest-Laptop; die Gäste brauchen
   eigenes Netz (Venue-WLAN oder Mobilfunk).
3. **Untertitel-only-Modus** bleibt bei TTS-Problemen automatisch verfügbar.
4. Kritischster Punkt ist das **Gäste-WLAN im Großen Saal** für 200 gleichzeitige
   Streams — vorab mit der Elbphilharmonie klären; Mobilfunk im Saal ist ggf. schwach.

### DSGVO

- Alles läuft auf dem eigenen Hetzner-Server (DE/FIN, AVV mit Hetzner).
- Audio wird nur im RAM segmentweise verarbeitet, standardmäßig **nicht gespeichert**
  (`NEX26_RECORD=0`). Transkript-Log optional abschaltbar.
- Einzige externe Verarbeitung: DeepL API (deutscher Anbieter, AVV verfügbar).
  Mit `NEX26_TRANSLATOR=opus` bleibt alles vollständig on-premise.
- Hörer-Seite: keine Cookies, kein Tracking, keine Anmeldung.

## Entwicklung / Test ohne Modelle

```bash
pip install -r requirements.txt
NEX26_FAKE_PIPELINE=1 uvicorn server.main:app --port 8026
pytest tests/
```

`NEX26_FAKE_PIPELINE=1` ersetzt ASR/MT/TTS durch Stubs (Sinuston + Dummy-Text) —
zum Testen von Broadcast, UI und Ingest ohne GPU.

## Konfiguration (.env)

| Variable | Default | Bedeutung |
|---|---|---|
| `NEX26_INGEST_TOKEN` | – (Pflicht) | Shared Secret für /ws/ingest und /stage |
| `NEX26_WHISPER_MODEL` | `large-v3` | faster-whisper-Modell |
| `NEX26_DEVICE` | `auto` | `cuda` / `cpu` / `auto` |
| `NEX26_TRANSLATOR` | `deepl` | `deepl` / `opus` / `none` |
| `DEEPL_API_KEY` | – | nötig bei `deepl` |
| `NEX26_PIPER_VOICE` | `de_DE-thorsten-high` | Piper-Stimme |
| `NEX26_MAX_SEGMENT_S` | `7.0` | max. Segmentlänge (Latenz-Obergrenze) |
| `NEX26_SILENCE_S` | `0.6` | Stille, die ein Segment beendet |
| `NEX26_RECORD` | `0` | `1` = Transkript-Log nach `logs/` schreiben |
| `NEX26_FAKE_PIPELINE` | `0` | Stub-Pipeline für Tests |
| `NEX26_PUBLIC_URL` | `http://localhost:8026` | Basis-URL für /qr |
