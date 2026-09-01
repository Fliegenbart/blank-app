import os
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _bool(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    ingest_token: str = field(default_factory=lambda: os.environ.get("NEX26_INGEST_TOKEN", ""))
    whisper_model: str = field(default_factory=lambda: os.environ.get("NEX26_WHISPER_MODEL", "large-v3"))
    device: str = field(default_factory=lambda: os.environ.get("NEX26_DEVICE", "auto"))
    translator: str = field(default_factory=lambda: os.environ.get("NEX26_TRANSLATOR", "deepl"))
    deepl_api_key: str = field(default_factory=lambda: os.environ.get("DEEPL_API_KEY", ""))
    piper_voice: str = field(default_factory=lambda: os.environ.get("NEX26_PIPER_VOICE", "de_DE-thorsten-high"))
    piper_bin: str = field(default_factory=lambda: os.environ.get("NEX26_PIPER_BIN", "piper"))
    max_segment_s: float = field(default_factory=lambda: float(os.environ.get("NEX26_MAX_SEGMENT_S", "7.0")))
    silence_s: float = field(default_factory=lambda: float(os.environ.get("NEX26_SILENCE_S", "0.6")))
    record: bool = field(default_factory=lambda: _bool("NEX26_RECORD"))
    fake_pipeline: bool = field(default_factory=lambda: _bool("NEX26_FAKE_PIPELINE"))
    public_url: str = field(default_factory=lambda: os.environ.get("NEX26_PUBLIC_URL", "http://localhost:8026"))
    glossary_path: Path = field(default_factory=lambda: Path(os.environ.get("NEX26_GLOSSARY", str(BASE_DIR / "glossary.csv"))))
    log_dir: Path = field(default_factory=lambda: Path(os.environ.get("NEX26_LOG_DIR", str(BASE_DIR / "logs"))))

    # Audio-Format des Ingest-Streams
    sample_rate: int = 16000
    sample_width: int = 2  # s16le


settings = Settings()
