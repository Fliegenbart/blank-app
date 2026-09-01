"""Glossar: erzwungene Begriffsersetzungen (en -> de) + Whisper-Prompt."""
from __future__ import annotations

import csv
import re
from pathlib import Path


class Glossary:
    def __init__(self, entries: dict[str, str] | None = None) -> None:
        self.entries = entries or {}
        self._patterns = [
            (re.compile(rf"\b{re.escape(en)}\b", re.IGNORECASE), de)
            for en, de in sorted(self.entries.items(), key=lambda kv: -len(kv[0]))
        ]

    @classmethod
    def load(cls, path: Path) -> "Glossary":
        entries: dict[str, str] = {}
        if path.exists():
            with path.open(newline="", encoding="utf-8") as f:
                for row in csv.reader(f):
                    if len(row) >= 2 and row[0].strip() and not row[0].startswith("#"):
                        entries[row[0].strip()] = row[1].strip()
        return cls(entries)

    def apply(self, text: str) -> str:
        for pattern, de in self._patterns:
            text = pattern.sub(de, text)
        return text

    def whisper_prompt(self, limit: int = 40) -> str:
        """Eigennamen/Fachbegriffe als initial_prompt für bessere ASR-Erkennung."""
        terms = list(self.entries.keys())[:limit]
        return "Vocabulary: " + ", ".join(terms) + "." if terms else ""
