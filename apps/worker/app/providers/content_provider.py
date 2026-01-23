import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from functools import lru_cache
import structlog

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class ContentProvider(ABC):
    """Abstract base class for AI content generation."""

    @abstractmethod
    def generate_landing_page_content(
        self,
        brand_profile: Dict[str, Any],
        topic: str,
        reference_structure: Optional[Dict[str, Any]] = None,
        sections: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate content for a landing page."""
        pass

    @abstractmethod
    def generate_social_media_content(
        self,
        brand_profile: Dict[str, Any],
        topic: str,
        platforms: List[str],
        reference_structure: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate content for social media posts."""
        pass

    @abstractmethod
    def generate_email_content(
        self,
        brand_profile: Dict[str, Any],
        topic: str,
        email_type: str,
        reference_structure: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate content for an email."""
        pass


class MockContentProvider(ContentProvider):
    """Mock content provider for testing without API calls."""

    def generate_landing_page_content(
        self,
        brand_profile: Dict[str, Any],
        topic: str,
        reference_structure: Optional[Dict[str, Any]] = None,
        sections: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate mock landing page content."""
        brand_name = brand_profile.get("identity", {}).get("name", "Brand")
        tone_attrs = brand_profile.get("tone_of_voice", {}).get("attributes", ["professional"])

        # Determine section order from reference or defaults
        if reference_structure and reference_structure.get("section_order_pattern"):
            section_types = reference_structure["section_order_pattern"]
        elif sections:
            section_types = sections
        else:
            section_types = ["hero", "features", "testimonials", "cta"]

        generated_sections = []
        for section_type in section_types:
            if section_type == "hero":
                generated_sections.append({
                    "type": "hero",
                    "heading": f"{topic}",
                    "subheading": f"Discover how {brand_name} can help you achieve more.",
                    "cta_text": "Get Started",
                    "cta_url": "#signup",
                })
            elif section_type == "features":
                generated_sections.append({
                    "type": "features",
                    "heading": "Why Choose Us",
                    "items": [
                        {"title": "Easy to Use", "description": "Intuitive interface that anyone can master."},
                        {"title": "Powerful Results", "description": "See measurable improvements in your workflow."},
                        {"title": "Expert Support", "description": "Our team is here to help you succeed."},
                    ],
                })
            elif section_type == "testimonials":
                generated_sections.append({
                    "type": "testimonials",
                    "heading": "What Our Customers Say",
                    "items": [
                        {"quote": f"{brand_name} transformed how we work.", "author": "Happy Customer"},
                    ],
                })
            elif section_type == "cta":
                generated_sections.append({
                    "type": "cta",
                    "heading": "Ready to Get Started?",
                    "subheading": "Join thousands of satisfied customers today.",
                    "cta_text": "Start Free Trial",
                    "cta_url": "#signup",
                })

        return {
            "title": f"{topic} | {brand_name}",
            "meta_description": f"Learn about {topic} from {brand_name}.",
            "sections": generated_sections,
        }

    def generate_social_media_content(
        self,
        brand_profile: Dict[str, Any],
        topic: str,
        platforms: List[str],
        reference_structure: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate mock social media content."""
        brand_name = brand_profile.get("identity", {}).get("name", "Brand")

        posts = {}
        for platform in platforms:
            if platform == "twitter":
                posts[platform] = [{
                    "text": f"Excited to share our latest on {topic}! 🚀 #innovation #{brand_name.lower().replace(' ', '')}",
                    "character_count": 80,
                }]
            elif platform == "linkedin":
                posts[platform] = [{
                    "text": f"We're thrilled to announce {topic}. At {brand_name}, we believe in continuous improvement and innovation. What do you think about this development? #business #growth",
                    "character_count": 180,
                }]
            elif platform == "instagram":
                posts[platform] = [{
                    "text": f"✨ {topic} ✨\n\nStay tuned for more updates from {brand_name}!\n\n#inspiration #brand #innovation",
                    "hashtags": ["inspiration", "brand", "innovation"],
                }]
            elif platform == "facebook":
                posts[platform] = [{
                    "text": f"📣 Big news! We're excited to share {topic} with our community. Thank you for being part of the {brand_name} family!\n\nLearn more: [link]",
                }]

        return {
            "topic": topic,
            "platforms": posts,
            "suggested_posting_times": {
                "twitter": "9:00 AM, 12:00 PM, 5:00 PM",
                "linkedin": "8:00 AM, 12:00 PM",
                "instagram": "11:00 AM, 7:00 PM",
                "facebook": "9:00 AM, 1:00 PM",
            },
        }

    def generate_email_content(
        self,
        brand_profile: Dict[str, Any],
        topic: str,
        email_type: str,
        reference_structure: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate mock email content."""
        brand_name = brand_profile.get("identity", {}).get("name", "Brand")

        if email_type == "newsletter":
            return {
                "subject": f"📬 {brand_name} Newsletter: {topic}",
                "preview_text": f"The latest updates on {topic}",
                "greeting": "Hi there,",
                "body": [
                    f"We're excited to share the latest news about {topic}.",
                    "Here's what you need to know:",
                ],
                "sections": [
                    {"heading": "What's New", "content": f"Our latest updates on {topic}."},
                    {"heading": "Tips & Tricks", "content": "Helpful advice from our team."},
                ],
                "cta": {"text": "Learn More", "url": "#"},
                "closing": f"Best regards,\nThe {brand_name} Team",
            }
        elif email_type == "promotional":
            return {
                "subject": f"🎉 Special Offer: {topic}",
                "preview_text": f"Don't miss out on {topic}",
                "greeting": "Hello!",
                "body": [
                    f"We have an exciting offer for you regarding {topic}!",
                    "For a limited time, take advantage of this special opportunity.",
                ],
                "offer_details": f"Save on {topic}",
                "cta": {"text": "Claim Your Offer", "url": "#"},
                "closing": f"Don't miss out!\n{brand_name}",
            }
        else:  # announcement
            return {
                "subject": f"📢 Announcement: {topic}",
                "preview_text": f"Important news about {topic}",
                "greeting": "Dear valued customer,",
                "body": [
                    f"We have an important announcement regarding {topic}.",
                    "We wanted you to be the first to know.",
                ],
                "cta": {"text": "Read More", "url": "#"},
                "closing": f"Thank you for your continued support.\n{brand_name}",
            }


class OpenAIContentProvider(ContentProvider):
    """OpenAI-based content generation provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            logger.warning("OpenAI package not installed, falling back to mock")
            self.client = None

    def _get_brand_context(self, brand_profile: Dict[str, Any]) -> str:
        """Create brand context string from profile."""
        identity = brand_profile.get("identity", {})
        tone = brand_profile.get("tone_of_voice", {})

        context_parts = [
            f"Brand: {identity.get('name', 'Unknown')}",
        ]

        if identity.get("tagline"):
            context_parts.append(f"Tagline: {identity['tagline']}")

        if tone.get("attributes"):
            context_parts.append(f"Tone: {', '.join(tone['attributes'])}")

        if tone.get("do"):
            context_parts.append(f"Writing guidelines: {'; '.join(tone['do'][:3])}")

        if tone.get("example_phrases"):
            context_parts.append(f"Example phrases: {'; '.join(tone['example_phrases'][:3])}")

        return "\n".join(context_parts)

    def _get_reference_context(self, reference_structure: Optional[Dict[str, Any]]) -> str:
        """Create reference context string from structure."""
        if not reference_structure:
            return ""

        context_parts = ["Reference website analysis:"]

        if reference_structure.get("section_order_pattern"):
            context_parts.append(f"Section structure: {', '.join(reference_structure['section_order_pattern'])}")

        if reference_structure.get("key_messaging"):
            context_parts.append(f"Key messaging themes: {'; '.join(reference_structure['key_messaging'][:5])}")

        if reference_structure.get("content_themes"):
            context_parts.append(f"Content themes: {', '.join(reference_structure['content_themes'][:5])}")

        if reference_structure.get("cta_patterns"):
            context_parts.append(f"CTA patterns: {'; '.join(reference_structure['cta_patterns'][:3])}")

        return "\n".join(context_parts)

    def generate_landing_page_content(
        self,
        brand_profile: Dict[str, Any],
        topic: str,
        reference_structure: Optional[Dict[str, Any]] = None,
        sections: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate landing page content using OpenAI."""
        if not self.client:
            return MockContentProvider().generate_landing_page_content(
                brand_profile, topic, reference_structure, sections
            )

        brand_context = self._get_brand_context(brand_profile)
        reference_context = self._get_reference_context(reference_structure)

        # Determine sections
        if reference_structure and reference_structure.get("section_order_pattern"):
            section_list = reference_structure["section_order_pattern"]
        elif sections:
            section_list = sections
        else:
            section_list = ["hero", "features", "testimonials", "cta"]

        system_prompt = f"""You are a professional copywriter creating landing page content.

{brand_context}

{reference_context}

Generate engaging, on-brand content for a landing page about "{topic}".
Create content for these sections: {', '.join(section_list)}

Respond in JSON format with this structure:
{{
    "title": "Page title",
    "meta_description": "SEO description",
    "sections": [
        {{
            "type": "section_type",
            "heading": "Section heading",
            "subheading": "Optional subheading",
            "content": ["paragraph1", "paragraph2"],
            "items": [
                {{"title": "Item title", "description": "Item description"}}
            ],
            "cta_text": "Button text",
            "cta_url": "#"
        }}
    ]
}}

Generate unique, compelling content that matches the brand voice. Do not use placeholder text."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create landing page content for: {topic}"}
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error("OpenAI landing page generation failed", error=str(e))
            return MockContentProvider().generate_landing_page_content(
                brand_profile, topic, reference_structure, sections
            )

    def generate_social_media_content(
        self,
        brand_profile: Dict[str, Any],
        topic: str,
        platforms: List[str],
        reference_structure: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate social media content using OpenAI."""
        if not self.client:
            return MockContentProvider().generate_social_media_content(
                brand_profile, topic, platforms, reference_structure
            )

        brand_context = self._get_brand_context(brand_profile)
        reference_context = self._get_reference_context(reference_structure)

        platform_specs = {
            "twitter": "280 characters max, use hashtags, engaging and concise",
            "linkedin": "Professional tone, 1-3 paragraphs, industry-relevant hashtags",
            "instagram": "Visual-focused caption, use emojis, 5-10 relevant hashtags",
            "facebook": "Conversational, can be longer, encourage engagement",
        }

        specs_str = "\n".join([
            f"- {p}: {platform_specs.get(p, 'Standard format')}"
            for p in platforms
        ])

        system_prompt = f"""You are a social media content strategist.

{brand_context}

{reference_context}

Create engaging social media posts about "{topic}" for these platforms:
{specs_str}

Respond in JSON format:
{{
    "topic": "{topic}",
    "platforms": {{
        "platform_name": [
            {{
                "text": "Post content",
                "hashtags": ["hashtag1", "hashtag2"]
            }}
        ]
    }},
    "suggested_posting_times": {{
        "platform": "time recommendation"
    }}
}}

Create 2-3 variations for each platform. Match the brand voice exactly."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create social media content for: {topic}"}
                ],
                temperature=0.8,
                max_tokens=1500,
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error("OpenAI social media generation failed", error=str(e))
            return MockContentProvider().generate_social_media_content(
                brand_profile, topic, platforms, reference_structure
            )

    def generate_email_content(
        self,
        brand_profile: Dict[str, Any],
        topic: str,
        email_type: str,
        reference_structure: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate email content using OpenAI."""
        if not self.client:
            return MockContentProvider().generate_email_content(
                brand_profile, topic, email_type, reference_structure
            )

        brand_context = self._get_brand_context(brand_profile)
        reference_context = self._get_reference_context(reference_structure)

        email_specs = {
            "newsletter": "Informative, multiple sections, regular update format",
            "promotional": "Compelling offer, urgency, clear value proposition",
            "announcement": "News-focused, important update, professional tone",
            "welcome": "Warm, introductory, sets expectations",
            "followup": "Personal, action-oriented, builds relationship",
        }

        system_prompt = f"""You are an email marketing specialist.

{brand_context}

{reference_context}

Create an {email_type} email about "{topic}".
Email type characteristics: {email_specs.get(email_type, 'Standard format')}

Respond in JSON format:
{{
    "subject": "Email subject line",
    "preview_text": "Email preview text",
    "greeting": "Opening greeting",
    "body": ["paragraph1", "paragraph2"],
    "sections": [
        {{"heading": "Section heading", "content": "Section content"}}
    ],
    "cta": {{"text": "Button text", "url": "#"}},
    "closing": "Sign-off message"
}}

Create compelling, on-brand email content that drives action."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create {email_type} email content for: {topic}"}
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error("OpenAI email generation failed", error=str(e))
            return MockContentProvider().generate_email_content(
                brand_profile, topic, email_type, reference_structure
            )


@lru_cache()
def get_content_provider() -> ContentProvider:
    """Get the appropriate content provider based on configuration."""
    if settings.OPENAI_API_KEY:
        logger.info("Using OpenAI content provider")
        return OpenAIContentProvider(settings.OPENAI_API_KEY)
    else:
        logger.info("Using mock content provider")
        return MockContentProvider()
