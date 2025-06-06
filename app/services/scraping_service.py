import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingService:
    """
    Service responsible for fetching web content from URLs.
    """
    def scrape_website(self, url: str) -> str:
        """
        Fetches the HTML content of a given URL.
        """
        if not url or not url.startswith(('http://', 'https://')):
            logger.error(f"Invalid URL provided for scraping: {url}")
            raise ValueError("Invalid URL format. Must start with http:// or https://")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            logger.info(f"Successfully scraped URL: {url}")
            return response.text
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error scraping {url}: {e.response.status_code} - {e.response.reason}")
            raise ConnectionError(f"HTTP Error: {e.response.status_code}") from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error scraping {url}: {e}")
            raise ConnectionError(f"Network Connection Error: {e}") from e
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error scraping {url}: {e}")
            raise ConnectionError(f"Request Timed Out: {e}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"An unexpected request error occurred while scraping {url}: {e}")
            raise ConnectionError(f"Request Error: {e}") from e
        except Exception as e:
            logger.error(f"An unknown error occurred while scraping {url}: {e}")
            raise RuntimeError(f"Unexpected error during scraping: {e}") from e

    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parses HTML content using BeautifulSoup.
        """
        if not html_content:
            raise ValueError("HTML content cannot be empty for parsing.")
        return BeautifulSoup(html_content, 'html.parser')

# Example usage (for testing, will be called from API later)
if __name__ == '__main__':
    scraper = ScrapingService()
    test_url = "https://www.example.com" # Or any public company website

    try:
        html = scraper.scrape_website(test_url)
        soup = scraper.parse_html(html)
        print(f"Title: {soup.title.string if soup.title else 'No title found'}")
    except Exception as e:
        print(f"An error occurred: {e}")
