from bs4 import BeautifulSoup
import re
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataExtractionService:
    """
    Service responsible for extracting structured company information from parsed HTML.
    This is a simplified version; real-world extraction can be much more complex.
    """

    def extract_company_data(self, content: str, custom_instructions: str = None, data_sources: list = None) -> dict:
        """
        Extracts various pieces of company data from content (HTML or text).
        This method will contain heuristics and patterns for common data points.
        """
        # If content is HTML, parse it with BeautifulSoup
        if '<html' in content.lower() or '<body' in content.lower():
            soup = BeautifulSoup(content, 'html.parser')
        else:
            # Create a mock soup object for text content
            soup = BeautifulSoup(f"<html><body><p>{content}</p></body></html>", 'html.parser')
        data = {}

        # --- Basic Information ---
        data['name'] = self._extract_company_name(soup)
        data['website_url'] = self._extract_website_url(soup) # Usually the URL scraped itself, or canonical
        data['description'] = self._extract_description(soup)
        data['industry'] = self._extract_industry(soup) # Often hard to get precisely from a single page
        data['founding_date'] = self._extract_founding_date(soup)

        # --- Contact Information ---
        data['address'] = self._extract_address(soup)
        data['phone_number'] = self._extract_phone_number(soup)
        data['email'] = self._extract_email(soup)
        data['social_media_links'] = self._extract_social_media_links(soup)

        # --- Business Metrics & Details ---
        data['employee_count'] = self._extract_employee_count(soup)
        data['products_services'] = self._extract_products_services(soup) # More generic text
        data['mission_statement'] = self._extract_mission_statement(soup)

        # You would add more specific extraction methods for other fields:
        # data['revenue_range'] = self._extract_revenue_range(soup)
        # data['key_personnel'] = self._extract_key_personnel(soup)
        # data['certifications'] = self._extract_certifications(soup)
        # data['awards'] = self._extract_awards(soup)
        # data['recent_news_links'] = self._extract_recent_news_links(soup)
        # data['keywords'] = self._extract_keywords(soup)

        # Handle custom instructions
        if custom_instructions:
            data['custom_instructions_used'] = custom_instructions
            # Apply custom focus based on instructions
            data = self._apply_custom_instructions(data, soup, custom_instructions)
        
        # Add data source information
        if data_sources:
            data['data_sources'] = data_sources

        return data

    def _extract_company_name(self, soup: BeautifulSoup) -> str | None:
        """Attempts to extract company name from title, h1, or og:site_name."""
        title = soup.title.string if soup.title else None
        if title and ('|' in title or '-' in title): # Often "Page Title | Company Name"
            if '|' in title:
                parts = title.split('|')
                return parts[-1].strip() if parts[-1].strip() else parts[0].strip()
            elif '-' in title:
                parts = title.split('-')
                return parts[-1].strip() if parts[-1].strip() else parts[0].strip()

        # Look for opengraph site name
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name and og_site_name.get('content'):
            return og_site_name['content']

        # Look for an h1 tag that might contain the name
        h1 = soup.find('h1')
        if h1 and h1.string and len(h1.string) < 100: # Heuristic: H1 is usually short
            return h1.string.strip()

        logger.debug("Could not reliably extract company name.")
        return title.strip() if title else None # Fallback to full title if nothing better

    def _extract_website_url(self, soup: BeautifulSoup) -> str | None:
        """Extracts canonical URL or uses the base URL."""
        canonical_link = soup.find('link', rel='canonical')
        if canonical_link and canonical_link.get('href'):
            return canonical_link['href']
        # If not canonical, the URL that was scraped is usually the primary.
        # This function might be more useful if we're finding *other* websites.
        return None # Placeholder, the URL will come from the input

    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        """Extracts description from meta tags or a prominent paragraph."""
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description and meta_description.get('content'):
            return meta_description['content'].strip()

        # Fallback: look for a large paragraph, e.g., in a div with "about" in its id/class
        about_div = soup.find('div', class_=re.compile(r'about', re.I))
        if about_div:
            p = about_div.find('p')
            if p and p.string and len(p.string) > 50: # Heuristic: likely a description
                return p.string.strip()

        logger.debug("Could not extract a good description.")
        return None

    def _extract_industry(self, soup: BeautifulSoup) -> str | None:
        """
        Industry is very hard to extract reliably from a single page without NLP.
        Often inferred from content or context. This is a placeholder.
        """
        # Could look for keywords in page content, or in meta keywords.
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            return meta_keywords['content'].split(',')[0].strip() # Take the first keyword as potential industry

        # For a more advanced approach, you'd integrate an NLP model
        # or a lookup based on content analysis.
        logger.debug("Could not reliably extract industry.")
        return None

    def _extract_founding_date(self, soup: BeautifulSoup) -> str | None:
        """
        Attempts to find a founding date. This is highly heuristic.
        Looks for phrases like "established in", "founded in", followed by a year.
        """
        # Common patterns: "Founded in 1990", "Established in 2005"
        text = soup.get_text()
        matches = re.findall(r'(?:founded|established|since)\s+in\s+(\d{4})', text, re.I)
        if matches:
            return matches[0]
        logger.debug("Could not extract founding date.")
        return None

    def _extract_address(self, soup: BeautifulSoup) -> str | None:
        """
        Attempts to extract an address using common patterns or schema.org markup.
        This is a very simplified example. Real-world needs more robust parsing.
        """
        # Look for schema.org LocalBusiness or Organization markup
        schema_address = soup.find('script', type='application/ld+json', string=re.compile(r'address', re.I))
        if schema_address:
            try:
                json_ld = json.loads(schema_address.string)
                if isinstance(json_ld, list): # Sometimes it's an array
                    for item in json_ld:
                        if item.get('@type') in ['Organization', 'LocalBusiness'] and item.get('address'):
                            addr = item['address']
                            if isinstance(addr, dict) and addr.get('streetAddress'):
                                return f"{addr.get('streetAddress', '')}, {addr.get('addressLocality', '')}, {addr.get('addressRegion', '')} {addr.get('postalCode', '')}, {addr.get('addressCountry', '')}".strip(', ').replace(', ,', ',')
                elif isinstance(json_ld, dict) and json_ld.get('@type') in ['Organization', 'LocalBusiness'] and json_ld.get('address'):
                    addr = json_ld['address']
                    if isinstance(addr, dict) and addr.get('streetAddress'):
                        return f"{addr.get('streetAddress', '')}, {addr.get('addressLocality', '')}, {addr.get('addressRegion', '')} {addr.get('postalCode', '')}, {addr.get('addressCountry', '')}".strip(', ').replace(', ,', ',')
            except json.JSONDecodeError:
                logger.warning("Failed to decode JSON-LD for address.")

        # Look for common footer/contact section elements
        footer = soup.find('footer')
        contact_div = soup.find('div', class_=re.compile(r'contact|address', re.I))

        # Simple regex for address (e.g., something with a street number and street name)
        # This is highly unreliable for general use.
        address_patterns = [
            r'\d+\s+[\w\s]+\s+(?:street|st|road|rd|avenue|ave|drive|dr|lane|ln|boulevard|blvd|)(\W|$)',
            r'P\.O\.\s*Box\s*\d+',
            r'\d+\s+[\w\s]+,\s*[\w\s]+,\s*[\w\s]+\s*\d{5}' # Street, City, State Postal
        ]
        text_content = soup.get_text()
        for pattern in address_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        logger.debug("Could not reliably extract address.")
        return None


    def _extract_phone_number(self, soup: BeautifulSoup) -> str | None:
        """Extracts phone numbers using regex patterns."""
        text = soup.get_text()
        # Common phone number patterns (e.g., +1 (123) 456-7890, 123-456-7890, (123) 456-7890)
        phone_pattern = r'(?:\+\d{1,3}[-.●\s]?)?\(?\d{3}\)?[-\.●\s]?\d{3}[-\.●\s]?\d{4}(?!\d)'
        matches = re.findall(phone_pattern, text)
        if matches:
            # Return the first found, or could return a list
            return matches[0].strip()
        logger.debug("Could not extract phone number.")
        return None

    def _extract_email(self, soup: BeautifulSoup) -> str | None:
        """Extracts email addresses."""
        text = soup.get_text()
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        matches = re.findall(email_pattern, text)
        if matches:
            # Filter out common false positives like "example.com" domains
            valid_emails = [m for m in matches if 'example.com' not in m and 'domain.com' not in m]
            if valid_emails:
                return valid_emails[0].strip()
        logger.debug("Could not extract email.")
        return None

    def _extract_social_media_links(self, soup: BeautifulSoup) -> dict | None:
        """
        Extracts common social media links (LinkedIn, Twitter, Facebook, Instagram).
        Looks for links with specific keywords in href or class names.
        """
        social_links = {}
        link_patterns = {
            'linkedin': r'linkedin\.com',
            'twitter': r'twitter\.com|x\.com',
            'facebook': r'facebook\.com',
            'instagram': r'instagram\.com',
            'youtube': r'youtube\.com'
        }

        for link in soup.find_all('a', href=True):
            href = link['href']
            for platform, pattern in link_patterns.items():
                if re.search(pattern, href, re.IGNORECASE):
                    if platform not in social_links: # Only add the first one found for each platform
                        social_links[platform] = href
                        logger.debug(f"Found {platform} link: {href}")
        return social_links if social_links else None

    def _extract_employee_count(self, soup: BeautifulSoup) -> int | None:
        """
        Attempts to extract employee count from text. Very heuristic.
        Looks for phrases like "X employees", "over X people".
        """
        text = soup.get_text()
        patterns = [
            r'(\d{1,3}(?:,\d{3})*)[\+\-]?\s*(?:employees|staff|people|team)',
            r'(?:over|more than)\s+(\d{1,3}(?:,\d{3})*)\s*(?:employees|staff|people)',
            r'employee count:\s*(\d{1,3}(?:,\d{3})*)',
            r'(\d+)\s*employee(?:s)?'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1).replace(',', ''))
                except ValueError:
                    continue # Skip if conversion fails
        logger.debug("Could not extract employee count.")
        return None

    def _extract_products_services(self, soup: BeautifulSoup) -> str | None:
        """
        Attempts to extract a summary of products/services.
        Could look for sections titled "Products", "Services", "Solutions".
        """
        sections_to_check = ['products', 'services', 'solutions', 'offerings']
        for section_name in sections_to_check:
            # Find h1, h2, h3 that contains the section name
            heading = soup.find(re.compile(r'^h[1-3]$'), string=re.compile(section_name, re.I))
            if heading:
                # Get the next sibling elements (paragraphs, lists)
                content = []
                for sibling in heading.find_next_siblings():
                    if sibling.name in ['p', 'li']:
                        content.append(sibling.get_text(strip=True))
                    elif sibling.name and sibling.name.startswith('h'): # Stop at next heading
                        break
                    if len(" ".join(content)) > 500: # Limit length
                        break
                if content:
                    return "\n".join(content)

        # Fallback: Look for prominent lists that might contain services/products
        ul_elements = soup.find_all('ul', class_=re.compile(r'(?:product|service|solution)', re.I))
        if ul_elements:
            for ul in ul_elements:
                items = [li.get_text(strip=True) for li in ul.find_all('li') if li.get_text(strip=True)]
                if items:
                    return "\n".join(items)

        logger.debug("Could not extract products/services summary.")
        return None

    def _extract_mission_statement(self, soup: BeautifulSoup) -> str | None:
        """
        Attempts to extract a mission statement.
        Looks for common keywords near paragraph tags.
        """
        text = soup.get_text()
        # Look for "Our Mission", "Mission Statement", "Vision"
        mission_keywords = r'(?:our\s+mission|mission\s+statement|our\s+vision|vision\s+statement|our\s+values)'
        match = re.search(f'{mission_keywords}\s*(.*?)(?=\\n\\n|\\Z)', text, re.DOTALL | re.IGNORECASE) # Find text until next double newline
        if match:
            # Further refine to get content *after* the keyword, up to a certain length
            start_index = match.start()
            # Try to find the nearest paragraph after the keyword
            p_tags = soup.find_all('p')
            for p in p_tags:
                if soup.get_text().find(p.get_text(strip=True)) >= start_index: # If paragraph is after the keyword
                    return p.get_text(strip=True)

        logger.debug("Could not extract mission statement.")
        return None

    def _apply_custom_instructions(self, data: dict, soup: BeautifulSoup, instructions: str) -> dict:
        """
        Apply custom instructions to enhance data extraction based on user requirements.
        This method looks for specific keywords in instructions and extracts relevant data.
        """
        instructions_lower = instructions.lower()
        text_content = soup.get_text().lower()
        
        # Focus on technology stack if mentioned
        if any(keyword in instructions_lower for keyword in ['technology', 'tech stack', 'technical', 'programming', 'software', 'development']):
            tech_keywords = ['python', 'javascript', 'react', 'angular', 'vue', 'node.js', 'java', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'c++', 'c#']
            found_tech = [tech for tech in tech_keywords if tech in text_content]
            if found_tech:
                data['technology_stack'] = found_tech
        
        # Focus on funding if mentioned
        if any(keyword in instructions_lower for keyword in ['funding', 'investment', 'raised', 'capital', 'venture', 'seed', 'series']):
            funding_patterns = [
                r'raised\s+\$?(\d+(?:\.\d+)?)\s*(?:million|m|billion|b|k|thousand)',
                r'funding\s+(?:of\s+)?\$?(\d+(?:\.\d+)?)\s*(?:million|m|billion|b|k|thousand)',
                r'series\s+[a-z]\s+.*?\$?(\d+(?:\.\d+)?)\s*(?:million|m|billion|b|k|thousand)'
            ]
            for pattern in funding_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    data['funding_information'] = matches
                    break
        
        # Focus on leadership if mentioned
        if any(keyword in instructions_lower for keyword in ['leadership', 'management', 'team', 'founders', 'ceo', 'executive']):
            leadership_patterns = [
                r'(ceo|chief executive officer):\s*([^,\n]+)',
                r'(cto|chief technology officer):\s*([^,\n]+)',
                r'(cfo|chief financial officer):\s*([^,\n]+)',
                r'founded by\s+([^,\n]+)',
                r'co-founder[s]?:\s*([^,\n]+)'
            ]
            leadership_info = {}
            for pattern in leadership_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        leadership_info[match[0]] = match[1].strip()
            if leadership_info:
                data['leadership_team'] = leadership_info
        
        # Focus on products/services if mentioned
        if any(keyword in instructions_lower for keyword in ['products', 'services', 'offerings', 'solutions', 'platform']):
            # Enhanced product/service extraction
            product_indicators = ['product', 'service', 'solution', 'platform', 'tool', 'application', 'software']
            enhanced_products = []
            for indicator in product_indicators:
                pattern = rf'{indicator}[s]?[:\-]?\s*([^,\n\.]+)'
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                enhanced_products.extend([match.strip() for match in matches if len(match) > 3])
            if enhanced_products:
                data['enhanced_products_services'] = list(set(enhanced_products))
        
        # Add focused description based on instructions
        if data.get('description'):
            data['custom_focused_description'] = f"Based on focus on {instructions}: {data['description']}"
        
        return data

# Example Usage (for testing, will be called from API later)
if __name__ == '__main__':
    from scraping_service import ScrapingService
    scraper = ScrapingService()
    extractor = DataExtractionService()

    # Use a real website for better testing
    test_url = "https://www.google.com/about/our-story/" # Example URL for a company with an "about" page
    # test_url = "https://www.microsoft.com/en-us/about"

    try:
        html = scraper.scrape_website(test_url)
        soup = scraper.parse_html(html)
        extracted_data = extractor.extract_company_data(soup)
        print("\n--- Extracted Data ---")
        for key, value in extracted_data.items():
            if value: # Only print non-empty values
                print(f"{key}: {value}")
    except Exception as e:
        print(f"An error occurred: {e}")

