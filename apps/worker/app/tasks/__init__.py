from app.tasks.analyze import analyze_upload
from app.tasks.generate import (
    generate_website,
    generate_newsletter,
    generate_landing_page,
    generate_social_media,
    generate_email,
)
from app.tasks.scrape import scrape_reference
from app.tasks.theme_generate import (
    generate_flyer,
    generate_brochure,
    generate_teaser_script,
    generate_presentation,
    generate_banner_ads,
)
from app.tasks.export import (
    export_print_pdf,
    export_figma,
)

__all__ = [
    "analyze_upload",
    "generate_website",
    "generate_newsletter",
    "generate_landing_page",
    "generate_social_media",
    "generate_email",
    "scrape_reference",
    # Theme asset generators
    "generate_flyer",
    "generate_brochure",
    "generate_teaser_script",
    "generate_presentation",
    "generate_banner_ads",
    # Export tasks
    "export_print_pdf",
    "export_figma",
]
