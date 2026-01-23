import io
import json
import zipfile
from typing import Dict, Any, List, Optional
import structlog

from app.providers.content_provider import get_content_provider

logger = structlog.get_logger()


class SocialMediaGenerator:
    """Generates social media content based on brand profile and reference structure."""

    def __init__(self):
        self.content_provider = get_content_provider()

    def generate(
        self,
        profile: Dict[str, Any],
        topic: str,
        platforms: List[str],
        reference_structure: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """Generate social media content zip file."""
        logger.info("Generating social media content", topic=topic, platforms=platforms)

        # Generate content using AI
        content = self.content_provider.generate_social_media_content(
            profile, topic, platforms, reference_structure
        )

        brand_name = profile.get("identity", {}).get("name", "Brand")

        # Create zip in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Generate content for each platform
            for platform in platforms:
                platform_content = content.get("platforms", {}).get(platform, [])
                if platform_content:
                    # Write posts as markdown
                    md_content = self._generate_platform_markdown(
                        platform, platform_content, profile
                    )
                    zf.writestr(f"{platform}/posts.md", md_content)

                    # Write posts as JSON
                    zf.writestr(f"{platform}/posts.json", json.dumps(platform_content, indent=2))

            # Write combined content.json
            zf.writestr("content.json", json.dumps(content, indent=2))

            # Generate social media guidelines
            guidelines = self._generate_guidelines(profile, content)
            zf.writestr("brand-guidelines.md", guidelines)

            # Generate README
            readme = self._generate_readme(profile, topic, platforms, content)
            zf.writestr("README.md", readme)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def _generate_platform_markdown(
        self,
        platform: str,
        posts: List[Dict[str, Any]],
        profile: Dict[str, Any],
    ) -> str:
        """Generate markdown file for platform posts."""
        brand_name = profile.get("identity", {}).get("name", "Brand")

        platform_names = {
            "twitter": "Twitter/X",
            "linkedin": "LinkedIn",
            "instagram": "Instagram",
            "facebook": "Facebook",
        }

        lines = [
            f"# {platform_names.get(platform, platform.title())} Posts",
            f"",
            f"**Brand:** {brand_name}",
            f"",
            "---",
            "",
        ]

        for i, post in enumerate(posts, 1):
            lines.append(f"## Post {i}")
            lines.append("")

            text = post.get("text", "")
            lines.append("```")
            lines.append(text)
            lines.append("```")
            lines.append("")

            if post.get("hashtags"):
                lines.append(f"**Hashtags:** {' '.join(['#' + h for h in post['hashtags']])}")
                lines.append("")

            if post.get("character_count"):
                lines.append(f"**Character Count:** {post['character_count']}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _generate_guidelines(self, profile: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Generate brand guidelines for social media."""
        brand_name = profile.get("identity", {}).get("name", "Brand")
        tone = profile.get("tone_of_voice", {})
        colors = profile.get("colors", {})

        primary_color = colors.get("primary", {}).get("hex", "#0066CC")
        attributes = tone.get("attributes", ["professional"])
        do_guidelines = tone.get("do", [])
        dont_guidelines = tone.get("dont", [])

        posting_times = content.get("suggested_posting_times", {})

        lines = [
            f"# {brand_name} Social Media Brand Guidelines",
            "",
            "## Brand Voice",
            "",
            f"**Tone Attributes:** {', '.join(attributes)}",
            "",
            "### Do",
            "",
        ]

        for guideline in do_guidelines[:5]:
            lines.append(f"- {guideline}")

        lines.extend([
            "",
            "### Don't",
            "",
        ])

        for guideline in dont_guidelines[:5]:
            lines.append(f"- {guideline}")

        lines.extend([
            "",
            "## Visual Guidelines",
            "",
            f"**Primary Brand Color:** {primary_color}",
            "",
            "When creating visual content:",
            "- Use brand colors consistently",
            "- Maintain visual hierarchy",
            "- Ensure text is readable on all backgrounds",
            "",
            "## Suggested Posting Times",
            "",
        ])

        for platform, time in posting_times.items():
            lines.append(f"- **{platform.title()}:** {time}")

        lines.extend([
            "",
            "## Hashtag Strategy",
            "",
            "- Use 3-5 relevant hashtags on Twitter",
            "- Use 5-10 hashtags on Instagram",
            "- Use 3-5 professional hashtags on LinkedIn",
            "- Avoid overusing hashtags on Facebook",
            "",
            "## Engagement Guidelines",
            "",
            "- Respond to comments within 24 hours",
            "- Thank users for positive feedback",
            "- Address concerns professionally and promptly",
            "- Maintain consistent brand voice in all interactions",
        ])

        return "\n".join(lines)

    def _generate_readme(
        self,
        profile: Dict[str, Any],
        topic: str,
        platforms: List[str],
        content: Dict[str, Any],
    ) -> str:
        """Generate README for the social media output."""
        brand_name = profile.get("identity", {}).get("name", "Brand")

        platform_file_list = "\n".join([
            f"- `{p}/posts.md` - {p.title()} posts in markdown\n- `{p}/posts.json` - {p.title()} posts as JSON"
            for p in platforms
        ])

        return f"""# {brand_name} Social Media Content

Generated social media content for "{topic}"

## Platforms

{', '.join([p.title() for p in platforms])}

## Files

{platform_file_list}
- `content.json` - All content combined
- `brand-guidelines.md` - Social media brand guidelines

## Usage

1. Review the generated posts in each platform folder
2. Customize content as needed for your specific campaign
3. Copy posts to your social media management tool
4. Schedule according to suggested posting times

## Brand Profile Applied

- **Primary Color:** {profile.get('colors', {}).get('primary', {}).get('hex', 'N/A')}
- **Tone:** {', '.join(profile.get('tone_of_voice', {}).get('attributes', ['N/A']))}

## Best Practices

- Always preview posts before publishing
- Test hashtags for relevance and reach
- Adapt content for current trends when appropriate
- Monitor engagement and adjust strategy accordingly
"""
