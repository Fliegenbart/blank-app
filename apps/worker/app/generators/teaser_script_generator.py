"""Teaser script generator for theme assets."""
import io
import zipfile
from typing import Dict, Any
import structlog

from app.providers.content_provider import get_content_provider

logger = structlog.get_logger()


class TeaserScriptGenerator:
    """Generates video teaser script in markdown and structured format."""

    def __init__(self):
        self.content_provider = get_content_provider()

    def generate(self, context: Dict[str, Any]) -> bytes:
        """Generate a teaser script zip file with markdown and JSON."""
        profile = context.get("profile", {})
        theme = context.get("theme", {})

        logger.info("Generating teaser script", theme=theme.get("name"))

        # Generate content using AI
        content = self._generate_content(profile, theme)

        # Create zip in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Main script in markdown
            markdown = self._generate_markdown(profile, theme, content)
            zf.writestr("script.md", markdown)

            # Structured script for production
            import json
            zf.writestr("script.json", json.dumps(content, indent=2))

            # Shot list
            shot_list = self._generate_shot_list(content)
            zf.writestr("shot-list.md", shot_list)

            # README
            readme = self._generate_readme(theme, content)
            zf.writestr("README.md", readme)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def _generate_content(self, profile: Dict[str, Any], theme: Dict[str, Any]) -> Dict[str, Any]:
        """Generate teaser script content using AI."""
        theme_name = theme.get("name", "Event")
        theme_desc = theme.get("description", "")
        brand_name = profile.get("identity", {}).get("name", "Brand")
        tone = profile.get("tone_of_voice", {})
        tone_attrs = tone.get("attributes", []) if isinstance(tone, dict) else []

        doc_context = ""
        for doc in theme.get("documents", []):
            if doc.get("text"):
                doc_context += f"\n{doc['name']}:\n{doc['text'][:1500]}\n"

        prompt = f"""Create a 30-60 second video teaser script for "{theme_name}".

Brand: {brand_name}
Theme Description: {theme_desc}
Brand Tone: {', '.join(tone_attrs) if tone_attrs else 'Professional, engaging'}
{f"Additional Context: {doc_context}" if doc_context else ""}

Generate JSON with:
{{
  "title": "Script title",
  "duration": "30-60 seconds",
  "style": "Cinematic/Dynamic/Minimal/etc",
  "mood": "Exciting/Inspiring/etc",
  "music_suggestion": "Type of music",
  "scenes": [
    {{
      "number": 1,
      "duration": "5s",
      "visual": "Description of what we see",
      "audio": "Voiceover/sound effects",
      "text_overlay": "On-screen text if any",
      "transition": "Cut/Fade/etc"
    }}
  ],
  "voiceover_full": "Complete voiceover script",
  "cta": {{
    "text": "Call to action",
    "url": "Website or action"
  }},
  "production_notes": "Additional notes for production"
}}

Create 5-8 scenes that build tension and excitement."""

        try:
            result = self.content_provider.generate_json(prompt)
            return result
        except Exception as e:
            logger.error("Content generation failed, using defaults", error=str(e))
            return self._default_content(theme_name, brand_name)

    def _default_content(self, theme_name: str, brand_name: str) -> Dict[str, Any]:
        """Return default content."""
        return {
            "title": f"{theme_name} Teaser",
            "duration": "30 seconds",
            "style": "Dynamic",
            "mood": "Exciting",
            "music_suggestion": "Upbeat corporate music with building momentum",
            "scenes": [
                {
                    "number": 1,
                    "duration": "3s",
                    "visual": "Brand logo animation on dark background",
                    "audio": "Music fades in",
                    "text_overlay": brand_name,
                    "transition": "Fade"
                },
                {
                    "number": 2,
                    "duration": "5s",
                    "visual": "Quick cuts of event highlights or related imagery",
                    "audio": "Voiceover: 'Something big is coming...'",
                    "text_overlay": None,
                    "transition": "Quick cuts"
                },
                {
                    "number": 3,
                    "duration": "6s",
                    "visual": "People engaging, energy building",
                    "audio": "Voiceover: 'An experience like no other'",
                    "text_overlay": theme_name,
                    "transition": "Dynamic"
                },
                {
                    "number": 4,
                    "duration": "4s",
                    "visual": "Key moment or reveal",
                    "audio": "Music builds",
                    "text_overlay": "Coming Soon",
                    "transition": "Impact"
                },
                {
                    "number": 5,
                    "duration": "5s",
                    "visual": "Call to action with logo",
                    "audio": "Voiceover: 'Join us'",
                    "text_overlay": "Learn More",
                    "transition": "Fade out"
                }
            ],
            "voiceover_full": f"Something big is coming. {theme_name} - an experience like no other. Join us.",
            "cta": {
                "text": "Learn More",
                "url": "Visit our website"
            },
            "production_notes": "Focus on energy and anticipation. Use brand colors in graphics."
        }

    def _generate_markdown(self, profile: Dict[str, Any], theme: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Generate markdown script."""
        brand_name = profile.get("identity", {}).get("name", "Brand")

        scenes_md = ""
        for scene in content.get("scenes", []):
            scenes_md += f"""
### Scene {scene.get('number', '?')} ({scene.get('duration', 'N/A')})

**Visual:** {scene.get('visual', 'N/A')}

**Audio:** {scene.get('audio', 'N/A')}

{f"**Text Overlay:** {scene['text_overlay']}" if scene.get('text_overlay') else ""}

**Transition:** {scene.get('transition', 'Cut')}

---
"""

        return f"""# {content.get('title', theme.get('name', 'Teaser'))}

## Overview

| Property | Value |
|----------|-------|
| Duration | {content.get('duration', '30-60 seconds')} |
| Style | {content.get('style', 'Dynamic')} |
| Mood | {content.get('mood', 'Exciting')} |
| Brand | {brand_name} |

## Music Suggestion

{content.get('music_suggestion', 'Upbeat corporate music')}

## Scenes
{scenes_md}

## Complete Voiceover

> {content.get('voiceover_full', '')}

## Call to Action

**Text:** {content.get('cta', {}).get('text', 'Learn More')}

**Action:** {content.get('cta', {}).get('url', 'Visit website')}

## Production Notes

{content.get('production_notes', 'No additional notes.')}

---

*Generated for {theme.get('name', 'Theme')} by {brand_name}*
"""

    def _generate_shot_list(self, content: Dict[str, Any]) -> str:
        """Generate a shot list for production."""
        shots = ""
        total_duration = 0

        for scene in content.get("scenes", []):
            duration = scene.get("duration", "5s")
            try:
                seconds = int(duration.replace("s", "").strip())
            except:
                seconds = 5
            total_duration += seconds

            shots += f"""| {scene.get('number', '?')} | {duration} | {scene.get('visual', 'N/A')[:50]}... | {scene.get('transition', 'Cut')} |
"""

        return f"""# Shot List

## Overview

- **Total Scenes:** {len(content.get('scenes', []))}
- **Estimated Duration:** {total_duration}s

## Shots

| # | Duration | Visual | Transition |
|---|----------|--------|------------|
{shots}

## Equipment Notes

- Camera: 4K minimum
- Audio: Professional VO recording
- Graphics: Motion graphics for text overlays

## Checklist

- [ ] Location scouting
- [ ] Talent booking
- [ ] Equipment rental
- [ ] Music licensing
- [ ] Voiceover recording
- [ ] Post-production
- [ ] Color grading
- [ ] Sound mixing
- [ ] Final export
"""

    def _generate_readme(self, theme: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Generate README."""
        return f"""# {theme.get('name', 'Theme')} Teaser Script

## Files

- `script.md` - Full script in readable format
- `script.json` - Structured data for production tools
- `shot-list.md` - Production shot list and checklist

## Script Details

- **Duration:** {content.get('duration', '30-60 seconds')}
- **Style:** {content.get('style', 'Dynamic')}
- **Scenes:** {len(content.get('scenes', []))}

## How to Use

### For Creative Review
Open `script.md` to review the full script with all details.

### For Production
Use `script.json` to import into video production software or project management tools.

### For Shooting
Print `shot-list.md` for on-set reference.

## Voiceover

The complete voiceover text can be found in `script.md` under "Complete Voiceover".
Duration should match the total video length minus any silent portions.

## Music

{content.get('music_suggestion', 'See script for music suggestions')}

Consider licensing from:
- Epidemic Sound
- Artlist
- Musicbed
- PremiumBeat
"""
