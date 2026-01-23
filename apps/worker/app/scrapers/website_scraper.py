import re
import io
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import structlog

from playwright.sync_api import sync_playwright, Page, Browser
from bs4 import BeautifulSoup

from app.scrapers.models import (
    ScrapedPage,
    ScrapedSection,
    ReferenceStructure,
    SectionType,
)

logger = structlog.get_logger()


class WebsiteScraper:
    """Scrapes websites using Playwright for reference analysis."""

    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self._browser: Optional[Browser] = None

    def scrape_urls(self, urls: List[str], take_screenshots: bool = False) -> ReferenceStructure:
        """
        Scrape multiple URLs and return analyzed reference structure.

        Args:
            urls: List of URLs to scrape
            take_screenshots: Whether to capture screenshots

        Returns:
            ReferenceStructure with all scraped and analyzed data
        """
        logger.info("Starting website scrape", url_count=len(urls))

        pages = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )

            for url in urls:
                try:
                    page = context.new_page()
                    scraped = self._scrape_page(page, url, take_screenshots)
                    pages.append(scraped)
                    page.close()
                except Exception as e:
                    logger.error("Failed to scrape URL", url=url, error=str(e))
                    pages.append(ScrapedPage(url=url, title="", error=str(e)))

            browser.close()

        # Analyze the scraped pages
        structure = self._analyze_structure(pages)
        return structure

    def _scrape_page(self, page: Page, url: str, take_screenshot: bool = False) -> ScrapedPage:
        """Scrape a single page."""
        logger.info("Scraping page", url=url)

        page.goto(url, timeout=self.timeout, wait_until="networkidle")
        page.wait_for_load_state("domcontentloaded")

        # Get page content
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Extract title
        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Extract meta description
        meta_desc = None
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag:
            meta_desc = meta_tag.get("content")

        # Extract text content
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        text_content = soup.get_text(separator=" ", strip=True)
        text_content = re.sub(r"\s+", " ", text_content)
        word_count = len(text_content.split())

        # Extract navigation
        navigation = self._extract_navigation(soup, url)

        # Extract sections
        sections = self._extract_sections(soup)

        # Take screenshot if requested
        screenshot_path = None
        if take_screenshot:
            screenshot_bytes = page.screenshot(full_page=True)
            # Note: Store screenshot via storage service if needed

        return ScrapedPage(
            url=url,
            title=title,
            meta_description=meta_desc,
            sections=sections,
            navigation=navigation,
            text_content=text_content[:10000],  # Limit text content
            word_count=word_count,
            screenshot_path=screenshot_path,
        )

    def _extract_navigation(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract navigation links from the page."""
        nav_items = []

        # Look for nav elements
        nav_elements = soup.find_all("nav")
        for nav in nav_elements:
            links = nav.find_all("a")
            for link in links:
                href = link.get("href", "")
                text = link.get_text(strip=True)
                if href and text:
                    full_url = urljoin(base_url, href)
                    nav_items.append({"text": text, "url": full_url})

        # Also check header for links
        header = soup.find("header")
        if header:
            links = header.find_all("a")
            for link in links:
                href = link.get("href", "")
                text = link.get_text(strip=True)
                if href and text and not any(n["text"] == text for n in nav_items):
                    full_url = urljoin(base_url, href)
                    nav_items.append({"text": text, "url": full_url})

        return nav_items[:20]  # Limit navigation items

    def _extract_sections(self, soup: BeautifulSoup) -> List[ScrapedSection]:
        """Extract sections from the page structure."""
        sections = []
        order = 0

        # Look for semantic sections
        section_elements = soup.find_all(["section", "article", "main", "aside"])

        for element in section_elements:
            section = self._parse_section(element, order)
            if section:
                sections.append(section)
                order += 1

        # If no sections found, try to identify by common class names
        if not sections:
            sections = self._extract_sections_by_classes(soup)

        # Always try to extract hero if not found
        if not any(s.section_type == SectionType.HERO for s in sections):
            hero = self._extract_hero(soup)
            if hero:
                hero.order = 0
                sections.insert(0, hero)

        return sections

    def _parse_section(self, element, order: int) -> Optional[ScrapedSection]:
        """Parse a section element into a ScrapedSection."""
        # Determine section type from classes or content
        classes = element.get("class", [])
        class_str = " ".join(classes).lower() if classes else ""
        section_id = (element.get("id") or "").lower()

        section_type = self._identify_section_type(class_str, section_id, element)

        # Extract heading
        heading = None
        heading_tag = element.find(["h1", "h2", "h3"])
        if heading_tag:
            heading = heading_tag.get_text(strip=True)

        # Extract subheading (usually next p after heading)
        subheading = None
        if heading_tag:
            next_p = heading_tag.find_next_sibling("p")
            if next_p:
                subheading = next_p.get_text(strip=True)[:200]

        # Extract content paragraphs
        content = []
        for p in element.find_all("p", limit=5):
            text = p.get_text(strip=True)
            if text and len(text) > 20:
                content.append(text[:500])

        # Extract CTA
        cta_text = None
        cta_url = None
        cta_link = element.find("a", class_=lambda x: x and any(
            c in (x if isinstance(x, str) else " ".join(x)).lower()
            for c in ["btn", "button", "cta"]
        ))
        if cta_link:
            cta_text = cta_link.get_text(strip=True)
            cta_url = cta_link.get("href")

        # Extract images
        images = []
        for img in element.find_all("img", limit=5):
            src = img.get("src") or img.get("data-src")
            if src:
                images.append(src)

        # Extract list items if present
        items = []
        for li in element.find_all("li", limit=10):
            item_text = li.get_text(strip=True)
            if item_text:
                items.append({"text": item_text[:200]})

        # Skip if too empty
        if not heading and not content and not images:
            return None

        return ScrapedSection(
            section_type=section_type,
            heading=heading,
            subheading=subheading,
            content=content,
            cta_text=cta_text,
            cta_url=cta_url,
            images=images,
            items=items,
            order=order,
            css_classes=classes if isinstance(classes, list) else [classes],
        )

    def _identify_section_type(self, class_str: str, section_id: str, element) -> SectionType:
        """Identify the type of section based on classes, id, and content."""
        combined = f"{class_str} {section_id}".lower()

        type_patterns = {
            SectionType.HERO: ["hero", "banner", "jumbotron", "masthead", "intro"],
            SectionType.FEATURES: ["feature", "benefit", "service", "capability"],
            SectionType.CTA: ["cta", "call-to-action", "action", "signup"],
            SectionType.TESTIMONIALS: ["testimonial", "review", "quote", "customer"],
            SectionType.PRICING: ["pricing", "plans", "packages", "subscription"],
            SectionType.TEAM: ["team", "people", "staff", "about-us"],
            SectionType.FAQ: ["faq", "questions", "accordion", "help"],
            SectionType.CONTACT: ["contact", "get-in-touch", "reach"],
            SectionType.FOOTER: ["footer", "site-footer"],
            SectionType.HEADER: ["header", "site-header", "top-bar"],
            SectionType.GALLERY: ["gallery", "portfolio", "showcase", "work"],
            SectionType.NAVIGATION: ["nav", "navigation", "menu"],
        }

        for section_type, patterns in type_patterns.items():
            if any(p in combined for p in patterns):
                return section_type

        # Check if it's content-heavy
        text_len = len(element.get_text(strip=True))
        if text_len > 500:
            return SectionType.CONTENT

        return SectionType.UNKNOWN

    def _extract_sections_by_classes(self, soup: BeautifulSoup) -> List[ScrapedSection]:
        """Extract sections by looking for common class patterns."""
        sections = []
        order = 0

        # Common section class patterns
        class_patterns = [
            "section", "block", "container", "wrapper",
            "hero", "features", "about", "services", "cta"
        ]

        for div in soup.find_all("div"):
            classes = div.get("class", [])
            if not classes:
                continue

            class_str = " ".join(classes).lower()
            if any(p in class_str for p in class_patterns):
                section = self._parse_section(div, order)
                if section:
                    sections.append(section)
                    order += 1
                    if order >= 10:  # Limit sections
                        break

        return sections

    def _extract_hero(self, soup: BeautifulSoup) -> Optional[ScrapedSection]:
        """Try to extract hero section from page."""
        # Look for h1 as it's usually in the hero
        h1 = soup.find("h1")
        if not h1:
            return None

        heading = h1.get_text(strip=True)

        # Find parent that might be the hero container
        parent = h1.find_parent(["section", "div", "header"])
        subheading = None
        cta_text = None
        cta_url = None

        if parent:
            # Get subheading
            p = parent.find("p")
            if p:
                subheading = p.get_text(strip=True)[:200]

            # Get CTA
            cta = parent.find("a", class_=lambda x: x and "btn" in str(x).lower())
            if cta:
                cta_text = cta.get_text(strip=True)
                cta_url = cta.get("href")

        return ScrapedSection(
            section_type=SectionType.HERO,
            heading=heading,
            subheading=subheading,
            cta_text=cta_text,
            cta_url=cta_url,
        )

    def _analyze_structure(self, pages: List[ScrapedPage]) -> ReferenceStructure:
        """Analyze scraped pages to extract common patterns."""
        # Collect all sections
        all_sections = []
        for page in pages:
            all_sections.extend(page.sections)

        # Find common section types
        section_type_counts: Dict[SectionType, int] = {}
        for section in all_sections:
            section_type_counts[section.section_type] = section_type_counts.get(
                section.section_type, 0
            ) + 1

        # Get section types that appear in more than half the pages
        threshold = len(pages) / 2
        common_sections = [
            st for st, count in section_type_counts.items()
            if count >= threshold
        ]

        # Determine typical section order
        section_order_pattern = self._get_section_order_pattern(pages)

        # Extract key messaging (headings and CTAs)
        key_messaging = []
        cta_patterns = []
        for page in pages:
            for section in page.sections:
                if section.heading:
                    key_messaging.append(section.heading)
                if section.cta_text:
                    cta_patterns.append(section.cta_text)

        # Deduplicate and limit
        key_messaging = list(dict.fromkeys(key_messaging))[:20]
        cta_patterns = list(dict.fromkeys(cta_patterns))[:10]

        # Combine navigation
        all_nav = []
        for page in pages:
            all_nav.extend(page.navigation)
        navigation_structure = list({n["text"]: n for n in all_nav}.values())[:15]

        # Extract content themes
        content_themes = self._extract_themes(pages)

        # Calculate total word count
        total_word_count = sum(p.word_count for p in pages)

        return ReferenceStructure(
            pages=pages,
            common_sections=common_sections,
            section_order_pattern=section_order_pattern,
            key_messaging=key_messaging,
            navigation_structure=navigation_structure,
            content_themes=content_themes,
            cta_patterns=cta_patterns,
            total_word_count=total_word_count,
        )

    def _get_section_order_pattern(self, pages: List[ScrapedPage]) -> List[SectionType]:
        """Determine the typical order of sections."""
        if not pages:
            return []

        # Use the page with most sections as template
        template_page = max(pages, key=lambda p: len(p.sections))
        return [s.section_type for s in sorted(template_page.sections, key=lambda s: s.order)]

    def _extract_themes(self, pages: List[ScrapedPage]) -> List[str]:
        """Extract common content themes from pages."""
        # Simple keyword extraction from headings
        words = []
        for page in pages:
            for section in page.sections:
                if section.heading:
                    words.extend(section.heading.lower().split())

        # Filter out common words
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "up", "about",
            "into", "over", "after", "our", "your", "their", "we", "you",
        }

        word_counts: Dict[str, int] = {}
        for word in words:
            word = re.sub(r"[^a-z]", "", word)
            if word and word not in stopwords and len(word) > 3:
                word_counts[word] = word_counts.get(word, 0) + 1

        # Return top themes
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:10]]
