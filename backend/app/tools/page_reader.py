import logging
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from app.config import settings
from app.tools.source_validator import is_safe_url, sanitize_web_content

logger = logging.getLogger(__name__)


class PageReader:
    """Safely fetches and extracts readable text from web pages."""

    def __init__(self, timeout: int = settings.REQUEST_TIMEOUT_SECONDS, max_bytes: int = settings.MAX_CONTENT_LENGTH_BYTES):
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 ResearchLabBot/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def fetch_page(self, url: str) -> Dict[str, Any]:
        """
        Safely fetch and parse a web page.
        Returns a dict with title, text, status, and metadata.
        """
        # 1. SSRF Validation
        safe, reason = is_safe_url(url)
        if not safe:
            logger.warning(f"Blocked unsafe URL: {url}. Reason: {reason}")
            return {
                "url": url,
                "title": "",
                "text": "",
                "status": "failed",
                "error": f"URL rejected: {reason}",
                "publication_date": None
            }

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
                max_redirects=3,
                verify=True
            ) as client:
                response = await client.get(url)

                # Validate final redirect destination
                final_safe, final_reason = is_safe_url(str(response.url))
                if not final_safe:
                    return {
                        "url": url,
                        "title": "",
                        "text": "",
                        "status": "failed",
                        "error": f"Redirected to unsafe URL: {final_reason}",
                        "publication_date": None
                    }

                if response.status_code != 200:
                    return {
                        "url": url,
                        "title": "",
                        "text": "",
                        "status": "failed",
                        "error": f"HTTP status {response.status_code}",
                        "publication_date": None
                    }

                # Check content type
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type and "text/plain" not in content_type:
                    return {
                        "url": url,
                        "title": "",
                        "text": "",
                        "status": "failed",
                        "error": f"Unsupported content type: {content_type}",
                        "publication_date": None
                    }

                raw_html = response.text[:self.max_bytes]

            # 2. Parse HTML
            soup = BeautifulSoup(raw_html, "html.parser")

            # Remove unwanted tags
            for element in soup(["script", "style", "nav", "footer", "header", "noscript", "aside", "svg"]):
                element.decompose()

            # Extract title
            title = ""
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            elif soup.find("h1"):
                title = soup.find("h1").get_text().strip()

            # Extract publication date if available
            pub_date = None
            date_meta = soup.find("meta", {"property": "article:published_time"}) or \
                        soup.find("meta", {"name": "publication_date"}) or \
                        soup.find("meta", {"name": "date"})
            if date_meta and date_meta.get("content"):
                pub_date = date_meta["content"][:10]  # e.g., YYYY-MM-DD

            # Extract main article or paragraph text
            article_tag = soup.find("article") or soup.find("main")
            if article_tag:
                paragraphs = article_tag.find_all("p")
            else:
                paragraphs = soup.find_all("p")

            text_content = " ".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
            if not text_content:
                text_content = soup.get_text(separator=" ", strip=True)

            sanitized_text = sanitize_web_content(text_content)

            return {
                "url": url,
                "title": title or url,
                "text": sanitized_text,
                "status": "success",
                "error": None,
                "publication_date": pub_date
            }

        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching {url}")
            return {
                "url": url,
                "title": "",
                "text": "",
                "status": "failed",
                "error": f"Request timed out after {self.timeout}s",
                "publication_date": None
            }
        except Exception as e:
            logger.warning(f"Error fetching {url}: {str(e)}")
            return {
                "url": url,
                "title": "",
                "text": "",
                "status": "failed",
                "error": str(e),
                "publication_date": None
            }
