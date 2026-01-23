from app.tasks.analyze import analyze_upload
from app.tasks.generate import (
    generate_website,
    generate_newsletter,
    generate_landing_page,
    generate_social_media,
    generate_email,
)
from app.tasks.scrape import scrape_reference

__all__ = [
    "analyze_upload",
    "generate_website",
    "generate_newsletter",
    "generate_landing_page",
    "generate_social_media",
    "generate_email",
    "scrape_reference",
]
