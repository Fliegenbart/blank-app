import io
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from functools import lru_cache
import structlog

from PIL import Image
import numpy as np

from app.config import get_settings
from app.parsers.base import ExtractedImage

logger = structlog.get_logger()
settings = get_settings()


class VisionProvider(ABC):
    """Abstract base class for image/vision analysis providers."""

    @abstractmethod
    def analyze_imagery(self, images: List[ExtractedImage]) -> Dict[str, Any]:
        """Analyze imagery style from images."""
        pass


class MockVisionProvider(VisionProvider):
    """Mock provider that uses basic image analysis."""

    def analyze_imagery(self, images: List[ExtractedImage]) -> Dict[str, Any]:
        """Analyze imagery using basic heuristics."""
        logger.info("Analyzing imagery with MockVisionProvider", image_count=len(images))

        if not images:
            return self._get_default_imagery()

        # Analyze images
        style = self._detect_style(images)
        mood = self._detect_mood(images)
        motifs = self._detect_motifs(images)

        # Calculate confidence based on image count
        confidence = min(0.6, len(images) * 0.1)

        return {
            "style": style,
            "mood": mood,
            "motifs": motifs,
            "notes": None,
            "confidence": confidence,
        }

    def _detect_style(self, images: List[ExtractedImage]) -> str:
        """Detect if images are photos or illustrations."""
        photo_score = 0
        illustration_score = 0

        for img in images[:5]:
            try:
                pil_img = Image.open(io.BytesIO(img.data))
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")

                # Sample colors
                pixels = np.array(pil_img.resize((50, 50)))

                # Calculate color variance (photos tend to have more color variation)
                variance = np.var(pixels)

                # Count unique colors (illustrations often have fewer)
                unique_colors = len(set(tuple(p) for p in pixels.reshape(-1, 3)))

                # High variance and many colors suggests photo
                if variance > 2000 and unique_colors > 500:
                    photo_score += 1
                # Low color count suggests illustration
                elif unique_colors < 200:
                    illustration_score += 1
                else:
                    photo_score += 0.5
                    illustration_score += 0.5

            except Exception as e:
                logger.warning("Error analyzing image style", error=str(e))

        if photo_score > illustration_score * 1.5:
            return "photo"
        elif illustration_score > photo_score * 1.5:
            return "illustration"
        else:
            return "mixed"

    def _detect_mood(self, images: List[ExtractedImage]) -> List[str]:
        """Detect mood from images based on colors and brightness."""
        moods = []

        brightness_values = []
        saturation_values = []
        warmth_values = []

        for img in images[:5]:
            try:
                pil_img = Image.open(io.BytesIO(img.data))
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")

                # Resize for analysis
                pil_img.thumbnail((100, 100))
                pixels = np.array(pil_img)

                # Calculate brightness
                brightness = np.mean(pixels)
                brightness_values.append(brightness)

                # Calculate saturation (simplified)
                r, g, b = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]
                max_rgb = np.maximum(np.maximum(r, g), b)
                min_rgb = np.minimum(np.minimum(r, g), b)
                saturation = np.mean((max_rgb - min_rgb) / (max_rgb + 1))
                saturation_values.append(saturation)

                # Calculate warmth (red/blue ratio)
                warmth = np.mean(r) / (np.mean(b) + 1)
                warmth_values.append(warmth)

            except Exception:
                pass

        # Determine mood based on averages
        if brightness_values:
            avg_brightness = np.mean(brightness_values)
            avg_saturation = np.mean(saturation_values)
            avg_warmth = np.mean(warmth_values)

            # Brightness-based moods
            if avg_brightness > 180:
                moods.append("light")
                moods.append("clean")
            elif avg_brightness < 80:
                moods.append("dark")
                moods.append("dramatic")

            # Saturation-based moods
            if avg_saturation > 0.4:
                moods.append("vibrant")
            elif avg_saturation < 0.15:
                moods.append("minimal")
                moods.append("muted")

            # Warmth-based moods
            if avg_warmth > 1.3:
                moods.append("warm")
            elif avg_warmth < 0.8:
                moods.append("cool")

        if not moods:
            moods = ["professional", "balanced"]

        return list(set(moods))[:5]

    def _detect_motifs(self, images: List[ExtractedImage]) -> List[str]:
        """Detect common motifs (simplified - would need ML in production)."""
        # This is a placeholder - real implementation would use object detection
        motifs = []

        # Check image dimensions for aspect ratio patterns
        landscapes = 0
        portraits = 0

        for img in images:
            if img.width > img.height * 1.2:
                landscapes += 1
            elif img.height > img.width * 1.2:
                portraits += 1

        if landscapes > len(images) * 0.6:
            motifs.append("landscape-oriented")
        if portraits > len(images) * 0.6:
            motifs.append("portrait-oriented")

        # This is very basic - a real implementation would use:
        # - Object detection models
        # - Scene classification
        # - Face detection
        # - Logo detection

        return motifs

    def _get_default_imagery(self) -> Dict[str, Any]:
        """Return default imagery analysis."""
        return {
            "style": "mixed",
            "mood": ["professional"],
            "motifs": [],
            "notes": None,
            "confidence": 0.0,
        }


@lru_cache()
def get_vision_provider() -> VisionProvider:
    """Get the appropriate vision provider."""
    # For now, always use mock
    # Could add OpenAI Vision API integration here
    logger.info("Using mock vision provider")
    return MockVisionProvider()
