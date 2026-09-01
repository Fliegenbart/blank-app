"""Übersetzung EN -> DE. Whisper kann nur X->EN, daher eigene MT-Stufe.

Backends:
- deepl: DeepL API (beste Qualität, AVV möglich, ~0,00002 EUR/Zeichen)
- opus:  Helsinki-NLP/opus-mt-en-de lokal (vollständig on-premise)
- none:  Passthrough (Debug)
"""
from __future__ import annotations

import logging

import httpx

from .glossary import Glossary

log = logging.getLogger("nex26.mt")


class PassthroughTranslator:
    def translate(self, text: str) -> str:
        return text


class FakeTranslator:
    def translate(self, text: str) -> str:
        return f"[DE] {text}"


class DeepLTranslator:
    def __init__(self, api_key: str, glossary: Glossary) -> None:
        self.api_key = api_key
        self.glossary = glossary
        base = "https://api-free.deepl.com" if api_key.endswith(":fx") else "https://api.deepl.com"
        self.client = httpx.Client(base_url=base, timeout=10.0)

    def translate(self, text: str) -> str:
        try:
            r = self.client.post(
                "/v2/translate",
                headers={"Authorization": f"DeepL-Auth-Key {self.api_key}"},
                data={"text": text, "source_lang": "EN", "target_lang": "DE"},
            )
            r.raise_for_status()
            out = r.json()["translations"][0]["text"]
        except Exception:
            log.exception("DeepL request failed, passing through English text")
            return text
        return self.glossary.apply(out)


class OpusMTTranslator:
    """Lokales Helsinki-NLP-Modell via transformers (CPU-tauglich, ~50ms/Satz auf GPU)."""

    def __init__(self, glossary: Glossary) -> None:
        from transformers import MarianMTModel, MarianTokenizer  # lazy

        name = "Helsinki-NLP/opus-mt-en-de"
        log.info("Loading %s", name)
        self.tokenizer = MarianTokenizer.from_pretrained(name)
        self.model = MarianMTModel.from_pretrained(name)
        self.glossary = glossary

    def translate(self, text: str) -> str:
        batch = self.tokenizer([text], return_tensors="pt", truncation=True, max_length=512)
        generated = self.model.generate(**batch, max_length=512)
        out = self.tokenizer.decode(generated[0], skip_special_tokens=True)
        return self.glossary.apply(out)


def build_translator(kind: str, deepl_api_key: str, glossary: Glossary):
    if kind == "deepl":
        if not deepl_api_key:
            raise RuntimeError("NEX26_TRANSLATOR=deepl braucht DEEPL_API_KEY")
        return DeepLTranslator(deepl_api_key, glossary)
    if kind == "opus":
        return OpusMTTranslator(glossary)
    if kind == "none":
        return PassthroughTranslator()
    raise RuntimeError(f"Unbekannter Translator: {kind}")
