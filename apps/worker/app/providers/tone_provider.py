import re
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from functools import lru_cache
import structlog

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class ToneProvider(ABC):
    """Abstract base class for tone of voice analysis providers."""

    @abstractmethod
    def analyze_tone(self, text: str) -> Dict[str, Any]:
        """Analyze the tone of voice from text."""
        pass


class MockToneProvider(ToneProvider):
    """Mock provider that uses rule-based analysis."""

    # Keyword patterns for tone detection
    PATTERNS = {
        "professional": [
            r"\b(enterprise|solution|strategy|implementation|optimize)\b",
            r"\b(stakeholder|deliverable|roi|kpi)\b",
        ],
        "friendly": [
            r"\b(welcome|happy|love|great|awesome)\b",
            r"!+",
            r"\b(you|your|we|our)\b",
        ],
        "technical": [
            r"\b(api|sdk|framework|algorithm|database)\b",
            r"\b(deploy|integrate|configure|implement)\b",
        ],
        "innovative": [
            r"\b(innovative|cutting-edge|revolutionary|breakthrough)\b",
            r"\b(transform|disrupt|pioneer|leading)\b",
        ],
        "trustworthy": [
            r"\b(trust|reliable|secure|proven|certified)\b",
            r"\b(guarantee|ensure|protect|safe)\b",
        ],
        "energetic": [
            r"!{2,}",
            r"\b(exciting|amazing|incredible|powerful)\b",
            r"\b(boost|accelerate|supercharge|unleash)\b",
        ],
        "formal": [
            r"\b(therefore|furthermore|consequently|hereby)\b",
            r"\b(shall|must|require|mandate)\b",
        ],
        "casual": [
            r"\b(hey|hi|cool|awesome|yeah)\b",
            r"\b(gonna|wanna|kinda|stuff)\b",
        ],
    }

    def analyze_tone(self, text: str) -> Dict[str, Any]:
        """Analyze tone using pattern matching."""
        logger.info("Analyzing tone with MockToneProvider")

        if not text or len(text.strip()) < 10:
            return self._get_default_tone()

        text_lower = text.lower()

        # Score each attribute
        scores = {}
        for attribute, patterns in self.PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)
            scores[attribute] = score

        # Normalize scores
        max_score = max(scores.values()) if scores.values() else 1
        if max_score > 0:
            scores = {k: v / max_score for k, v in scores.items()}

        # Get top attributes (score > 0.3)
        attributes = [k for k, v in sorted(scores.items(), key=lambda x: -x[1]) if v > 0.3][:4]

        if not attributes:
            attributes = ["professional", "clear"]

        # Generate do/don't guidelines based on detected tone
        do_guidelines = self._generate_do_guidelines(attributes)
        dont_guidelines = self._generate_dont_guidelines(attributes)

        # Extract example phrases
        example_phrases = self._extract_example_phrases(text)

        # Calculate confidence
        confidence = min(1.0, len(text) / 1000) * (0.5 if attributes else 0.2)

        return {
            "attributes": attributes,
            "do": do_guidelines,
            "dont": dont_guidelines,
            "example_phrases": example_phrases,
            "confidence": confidence,
        }

    def _generate_do_guidelines(self, attributes: List[str]) -> List[str]:
        """Generate 'do' guidelines based on attributes."""
        guidelines = []

        guideline_map = {
            "professional": "Use clear, business-appropriate language",
            "friendly": "Address the reader directly using 'you' and 'your'",
            "technical": "Include specific technical details when relevant",
            "innovative": "Highlight unique and forward-thinking aspects",
            "trustworthy": "Back claims with evidence and specifics",
            "energetic": "Use active voice and dynamic verbs",
            "formal": "Maintain a structured and precise tone",
            "casual": "Keep language conversational and approachable",
        }

        for attr in attributes:
            if attr in guideline_map:
                guidelines.append(guideline_map[attr])

        if not guidelines:
            guidelines = ["Be clear and concise", "Focus on benefits to the reader"]

        return guidelines[:5]

    def _generate_dont_guidelines(self, attributes: List[str]) -> List[str]:
        """Generate 'don't' guidelines based on attributes."""
        guidelines = []

        # Opposite guidelines
        if "professional" in attributes:
            guidelines.append("Avoid slang or overly casual expressions")
        if "friendly" in attributes:
            guidelines.append("Don't be cold or impersonal")
        if "technical" in attributes:
            guidelines.append("Don't oversimplify to the point of inaccuracy")
        if "formal" in attributes:
            guidelines.append("Avoid contractions and informal language")
        if "casual" in attributes:
            guidelines.append("Don't be stiff or overly formal")
        if "trustworthy" in attributes:
            guidelines.append("Avoid making unsubstantiated claims")
        if "energetic" in attributes:
            guidelines.append("Don't be monotonous or passive")

        if not guidelines:
            guidelines = ["Avoid jargon without explanation", "Don't be overly verbose"]

        return guidelines[:5]

    def _extract_example_phrases(self, text: str) -> List[str]:
        """Extract notable phrases from the text."""
        phrases = []

        # Look for short, impactful sentences
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            # Good example phrases: 5-15 words, not too long
            words = sentence.split()
            if 4 <= len(words) <= 12:
                # Check if it seems like a slogan or key message
                if any(word.lower() in sentence.lower() for word in ["we", "our", "your", "you"]):
                    phrases.append(sentence)
                    if len(phrases) >= 5:
                        break

        return phrases

    def _get_default_tone(self) -> Dict[str, Any]:
        """Return default tone analysis."""
        return {
            "attributes": ["professional", "clear"],
            "do": ["Be clear and concise", "Use active voice"],
            "dont": ["Avoid jargon", "Don't be overly verbose"],
            "example_phrases": [],
            "confidence": 0.0,
        }


class OpenAIToneProvider(ToneProvider):
    """OpenAI-based tone analysis provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            logger.warning("OpenAI package not installed, falling back to mock")
            self.client = None

    def analyze_tone(self, text: str) -> Dict[str, Any]:
        """Analyze tone using OpenAI."""
        if not self.client:
            return MockToneProvider().analyze_tone(text)

        logger.info("Analyzing tone with OpenAI")

        # Truncate text if too long
        max_chars = 4000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a brand voice analyst. Analyze the given text and extract:
1. attributes: 3-5 tone attributes (e.g., professional, friendly, innovative)
2. do: 3-5 writing guidelines (what to do)
3. dont: 3-5 things to avoid
4. example_phrases: 3-5 notable phrases from the text

Respond in JSON format:
{
    "attributes": ["attr1", "attr2", ...],
    "do": ["guideline1", "guideline2", ...],
    "dont": ["avoid1", "avoid2", ...],
    "example_phrases": ["phrase1", "phrase2", ...]
}"""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze the tone of this text:\n\n{text}"
                    }
                ],
                temperature=0.3,
                max_tokens=500,
            )

            import json
            result = json.loads(response.choices[0].message.content)
            result["confidence"] = 0.8

            return result

        except Exception as e:
            logger.error("OpenAI tone analysis failed", error=str(e))
            # Fallback to mock
            return MockToneProvider().analyze_tone(text)


@lru_cache()
def get_tone_provider() -> ToneProvider:
    """Get the appropriate tone provider based on configuration."""
    if settings.OPENAI_API_KEY:
        logger.info("Using OpenAI tone provider")
        return OpenAIToneProvider(settings.OPENAI_API_KEY)
    else:
        logger.info("Using mock tone provider")
        return MockToneProvider()
