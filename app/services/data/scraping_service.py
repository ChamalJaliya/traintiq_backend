import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
import time
from concurrent.futures import ThreadPoolExecutor
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedScrapingService:
    """
    Enhanced service for sophisticated web scraping with multiple strategies
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.selenium_options = self._setup_selenium_options()
        
    def _setup_selenium_options(self):
        """Setup Chrome options for Selenium"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')  # Can be enabled if needed
        return options

    async def scrape_multiple_urls(self, urls: List[str], custom_instructions: str = None) -> Dict[str, Any]:
        """
        Scrape multiple URLs concurrently and extract comprehensive company data
        """
        results = {
            'scraped_data': {},
            'failed_urls': [],
            'summary': {},
            'extraction_metadata': {}
        }
        
        # Filter valid URLs
        valid_urls = [url for url in urls if self._is_valid_url(url)]
        if not valid_urls:
            raise ValueError("No valid URLs provided")
        
        # Use ThreadPoolExecutor for concurrent scraping
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.scrape_website_enhanced, url): url for url in valid_urls}
            
            for future in futures:
                url = futures[future]
                try:
                    scraped_content, metadata = future.result(timeout=30)
                    results['scraped_data'][url] = scraped_content
                    results['extraction_metadata'][url] = metadata
                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")
                    results['failed_urls'].append({'url': url, 'error': str(e)})
        
        # Generate summary of all scraped content
        results['summary'] = self._generate_scraping_summary(results['scraped_data'])
        
        return results

    def scrape_website_enhanced(self, url: str, use_selenium: bool = False) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Enhanced website scraping with fallback mechanisms and comprehensive data extraction
        """
        if not self._is_valid_url(url):
            raise ValueError("Invalid URL format")

        metadata = {
            'url': url,
            'scraping_method': 'requests',
            'timestamp': time.time(),
            'success': False,
            'response_time': 0,
            'content_length': 0,
            'status_code': None
        }

        start_time = time.time()
        
        try:
            # Try standard requests first
            html_content = self._scrape_with_requests(url, metadata)
            
            # Temporarily disable Selenium fallback to avoid hanging
            # if not html_content or len(html_content) < 500:  # Minimal content threshold
            #     logger.info(f"Minimal content detected for {url}, trying Selenium...")
            #     html_content = self._scrape_with_selenium(url, metadata)
            #     metadata['scraping_method'] = 'selenium'
            
            if not html_content:
                raise Exception("No content extracted from any method")
            
            # Extract comprehensive data
            extracted_data = self._extract_comprehensive_data(html_content, url)
            metadata['success'] = True
            metadata['response_time'] = time.time() - start_time
            metadata['content_length'] = len(html_content)
            
            return extracted_data, metadata
            
        except Exception as e:
            logger.error(f"Enhanced scraping failed for {url}: {e}")
            metadata['error'] = str(e)
            metadata['response_time'] = time.time() - start_time
            raise e

    def _scrape_with_requests(self, url: str, metadata: Dict[str, Any]) -> str:
        """Scrape using requests library"""
        try:
            logger.info(f"Attempting to scrape {url} with requests...")
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            metadata['status_code'] = response.status_code
            logger.info(f"Successfully got response from {url}, status: {response.status_code}")
            
            # Check if content is HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"Non-HTML content type for {url}: {content_type}")
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Requests scraping failed for {url}: {e}")
            raise e

    def _scrape_with_selenium(self, url: str, metadata: Dict[str, Any]) -> str:
        """Scrape using Selenium for dynamic content"""
        driver = None
        try:
            driver = webdriver.Chrome(options=self.selenium_options)
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            html_content = driver.page_source
            return html_content
            
        except (TimeoutException, WebDriverException) as e:
            logger.error(f"Selenium scraping failed for {url}: {e}")
            raise e
        finally:
            if driver:
                driver.quit()

    def _extract_comprehensive_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract comprehensive company data from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        extracted_data = {
            'basic_info': self._extract_basic_company_info(soup, url),
            'contact_info': self._extract_enhanced_contact_information(soup, url),
            'business_info': self._extract_business_information(soup),
            'content_sections': self._extract_content_sections(soup),
            'structured_data': self._extract_structured_data(soup),
            'social_links': self._extract_social_media_links(soup),
            'raw_text': self._clean_extracted_text(soup.get_text()),
            'meta_information': self._extract_meta_information(soup),
            'logo_branding': self._extract_logo_and_branding(soup, url),
            'location_data': self._extract_location_data(soup),
            'technology_stack': self._extract_technology_mentions(soup),
            'people_entities': self._extract_people_entities(soup),
            'navigation_structure': self._extract_navigation_structure(soup),
            'structured_html': self._extract_structured_html_content(soup)
        }
        
        return extracted_data

    def _extract_basic_company_info(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract basic company information"""
        info = {}
        
        # Company name from various sources
        title = soup.find('title')
        if title:
            info['page_title'] = title.get_text().strip()
            # Extract company name from title
            title_text = title.get_text()
            if '|' in title_text:
                info['company_name'] = title_text.split('|')[-1].strip()
            elif '-' in title_text:
                info['company_name'] = title_text.split('-')[-1].strip()
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            info['description'] = meta_desc.get('content', '').strip()
        
        # OpenGraph data
        og_title = soup.find('meta', property='og:title')
        if og_title:
            info['og_title'] = og_title.get('content', '').strip()
        
        og_description = soup.find('meta', property='og:description')    
        if og_description:
            info['og_description'] = og_description.get('content', '').strip()
        
        # Domain information
        parsed_url = urlparse(url)
        info['domain'] = parsed_url.netloc
        info['source_url'] = url
        
        return info

    def _extract_contact_information(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract contact information"""
        contact_info = {}
        text_content = soup.get_text()
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text_content)
        if emails:
            contact_info['emails'] = list(set(emails))  # Remove duplicates
        
        # Phone numbers - enhanced patterns
        phone_patterns = [
            r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\+\d{1,3}[-.\s]?\d{1,14}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        
        all_phones = []
        for pattern in phone_patterns:
            phones = re.findall(pattern, text_content)
            all_phones.extend(phones)
        
        if all_phones:
            contact_info['phones'] = list(set([str(phone) for phone in all_phones]))
        
        # Address extraction - improved
        address_patterns = [
            r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)',
            r'P\.?O\.?\s*Box\s*\d+',
            r'\d+\s+[\w\s]+,\s*[\w\s]+,\s*[A-Z]{2}\s*\d{5}'
        ]
        
        addresses = []
        for pattern in address_patterns:
            found_addresses = re.findall(pattern, text_content, re.IGNORECASE)
            addresses.extend(found_addresses)
        
        if addresses:
            contact_info['addresses'] = list(set(addresses))
        
        return contact_info

    def _extract_business_information(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract business-specific information"""
        business_info = {}
        text_content = soup.get_text().lower()
        
        # Industry keywords detection
        industry_keywords = {
            'technology': ['software', 'tech', 'development', 'programming', 'digital', 'ai', 'machine learning'],
            'healthcare': ['medical', 'health', 'hospital', 'clinic', 'pharmaceutical'],
            'finance': ['financial', 'banking', 'investment', 'insurance', 'fintech'],
            'retail': ['retail', 'e-commerce', 'shopping', 'store', 'marketplace'],
            'manufacturing': ['manufacturing', 'production', 'factory', 'industrial'],
            'consulting': ['consulting', 'advisory', 'strategy', 'consulting services'],
            'education': ['education', 'training', 'learning', 'academic', 'university']
        }
        
        detected_industries = []
        for industry, keywords in industry_keywords.items():
            for keyword in keywords:
                if keyword in text_content:
                    detected_industries.append(industry)
                    break
        
        if detected_industries:
            business_info['detected_industries'] = list(set(detected_industries))
        
        # Services/Products detection
        service_indicators = ['services', 'solutions', 'products', 'offerings']
        services_section = None
        
        for indicator in service_indicators:
            # Look for headings containing service indicators
            heading = soup.find(['h1', 'h2', 'h3', 'h4'], string=re.compile(indicator, re.I))
            if heading:
                # Get the next sibling elements that might contain service descriptions
                services_section = heading.find_next_sibling()
                break
        
        if services_section:
            business_info['services_section'] = services_section.get_text().strip()
        
        return business_info

    def _extract_content_sections(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract different content sections"""
        sections = {}
        
        # Common section identifiers
        section_keywords = {
            'about': ['about', 'about us', 'company', 'overview'],
            'services': ['services', 'solutions', 'products', 'offerings'],
            'team': ['team', 'leadership', 'management', 'staff'],
            'contact': ['contact', 'reach us', 'get in touch'],
            'history': ['history', 'story', 'background'],
            'mission': ['mission', 'vision', 'values']
        }
        
        for section_name, keywords in section_keywords.items():
            for keyword in keywords:
                # Look for headings
                heading = soup.find(['h1', 'h2', 'h3', 'h4', 'h5'], 
                                  string=re.compile(rf'\b{keyword}\b', re.I))
                if heading:
                    # Extract content following the heading
                    content_elements = []
                    next_element = heading.find_next_sibling()
                    
                    while next_element and next_element.name not in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        if next_element.name in ['p', 'div', 'ul', 'ol']:
                            content_elements.append(next_element.get_text().strip())
                        next_element = next_element.find_next_sibling()
                    
                    if content_elements:
                        sections[section_name] = ' '.join(content_elements)
                        break
        
        return sections

    def _extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured data (JSON-LD, microdata)"""
        structured_data = {}
        
        # JSON-LD extraction
        json_scripts = soup.find_all('script', type='application/ld+json')
        json_ld_data = []
        
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                json_ld_data.append(data)
            except json.JSONDecodeError:
                continue
        
        if json_ld_data:
            structured_data['json_ld'] = json_ld_data
        
        # Microdata extraction (basic)
        microdata_elements = soup.find_all(attrs={'itemscope': True})
        if microdata_elements:
            microdata = []
            for element in microdata_elements:
                item_type = element.get('itemtype', '')
                if 'Organization' in item_type or 'LocalBusiness' in item_type:
                    microdata.append({
                        'type': item_type,
                        'properties': self._extract_microdata_properties(element)
                    })
            
            if microdata:
                structured_data['microdata'] = microdata
        
        return structured_data

    def _extract_microdata_properties(self, element) -> Dict[str, str]:
        """Extract microdata properties from an element"""
        properties = {}
        prop_elements = element.find_all(attrs={'itemprop': True})
        
        for prop_element in prop_elements:
            prop_name = prop_element.get('itemprop')
            prop_value = prop_element.get('content') or prop_element.get_text().strip()
            properties[prop_name] = prop_value
        
        return properties

    def _extract_social_media_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media links"""
        social_links = {}
        social_patterns = {
            'facebook': r'facebook\.com/[\w.-]+',
            'twitter': r'twitter\.com/[\w.-]+',
            'linkedin': r'linkedin\.com/[\w.-/]+',
            'instagram': r'instagram\.com/[\w.-]+',
            'youtube': r'youtube\.com/[\w.-/]+',
            'github': r'github\.com/[\w.-/]+'
        }
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            for platform, pattern in social_patterns.items():
                if re.search(pattern, href, re.I):
                    social_links[platform] = href
                    break
        
        return social_links

    def _extract_meta_information(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta information"""
        meta_info = {}
        
        # All meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_info[name] = content
        
        return meta_info

    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        return text.strip()

    def _generate_scraping_summary(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of scraped data"""
        summary = {
            'total_urls_scraped': len(scraped_data),
            'total_text_length': 0,
            'common_topics': [],
            'detected_company_names': [],
            'contact_methods_found': []
        }
        
        all_text = ""
        all_company_names = set()
        contact_methods = set()
        
        for url, data in scraped_data.items():
            if isinstance(data, dict):
                # Aggregate text
                if 'raw_text' in data:
                    all_text += data['raw_text'] + " "
                
                # Collect company names
                if 'basic_info' in data and 'company_name' in data['basic_info']:
                    all_company_names.add(data['basic_info']['company_name'])
                
                # Collect contact methods
                if 'contact_info' in data:
                    if 'emails' in data['contact_info']:
                        contact_methods.add('email')
                    if 'phones' in data['contact_info']:
                        contact_methods.add('phone')
                    if 'addresses' in data['contact_info']:
                        contact_methods.add('address')
        
        summary['total_text_length'] = len(all_text)
        summary['detected_company_names'] = list(all_company_names)
        summary['contact_methods_found'] = list(contact_methods)
        
        return summary

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except:
            return False

    def scrape_website(self, url: str) -> str:
        """Legacy method for backwards compatibility"""
        try:
            data, metadata = self.scrape_website_enhanced(url)
            return data.get('raw_text', '')
        except Exception as e:
            logger.error(f"Legacy scraping failed for {url}: {e}")
            raise e

    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse HTML content using BeautifulSoup - legacy method"""
        if not html_content:
            raise ValueError("HTML content cannot be empty for parsing.")
        return BeautifulSoup(html_content, 'html.parser')

    async def scrape_url_content(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a single URL - method expected by profile generator
        """
        try:
            extracted_data, metadata = self.scrape_website_enhanced(url)
            
            # Return in the format expected by profile generator
            return {
                'content': extracted_data.get('raw_text', ''),
                'title': extracted_data.get('basic_info', {}).get('title', ''),
                'url': url,
                'metadata': metadata,
                'structured_data': extracted_data
            }
            
        except Exception as e:
            logger.error(f"Failed to scrape URL content for {url}: {e}")
            return None

    def _extract_enhanced_contact_information(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Enhanced contact information extraction with NLP patterns"""
        contact_info = {}
        text_content = soup.get_text()
        
        # Enhanced email patterns
        email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'
        ]
        
        all_emails = []
        for pattern in email_patterns:
            emails = re.findall(pattern, text_content, re.IGNORECASE)
            all_emails.extend(emails)
        
        if all_emails:
            contact_info['emails'] = list(set(all_emails))
        
        # Enhanced phone number patterns (international support)
        phone_patterns = [
            r'\+\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # Simple US
            r'\+\d{1,3}\s\d{1,3}\s\d{3}\s\d{4}',  # Spaced international
            r'\d{4}[-.\s]?\d{3}[-.\s]?\d{3}'  # Alternative format
        ]
        
        all_phones = []
        for pattern in phone_patterns:
            phones = re.findall(pattern, text_content)
            all_phones.extend(phones)
        
        # Clean and validate phone numbers
        cleaned_phones = []
        for phone in all_phones:
            # Remove non-digit characters for validation
            digits_only = re.sub(r'\D', '', phone)
            if 7 <= len(digits_only) <= 15:  # Valid phone number length
                cleaned_phones.append(phone.strip())
        
        if cleaned_phones:
            contact_info['phones'] = list(set(cleaned_phones))
        
        return contact_info

    def _extract_logo_and_branding(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract logo and branding information"""
        branding_info = {}
        
        # Logo extraction patterns
        logo_selectors = [
            'img[alt*="logo" i]',
            'img[src*="logo" i]',
            'img[class*="logo" i]',
            '.logo img',
            '#logo img',
            'header img',
            '.brand img',
            '.navbar-brand img'
        ]
        
        logos = []
        for selector in logo_selectors:
            logo_elements = soup.select(selector)
            for logo in logo_elements:
                src = logo.get('src')
                if src:
                    # Convert relative URLs to absolute
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        from urllib.parse import urljoin
                        src = urljoin(url, src)
                    
                    logos.append({
                        'url': src,
                        'alt': logo.get('alt', ''),
                        'class': logo.get('class', [])
                    })
        
        if logos:
            branding_info['logos'] = logos
        
        return branding_info

    def _extract_location_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract location and geographic data"""
        location_data = {}
        text_content = soup.get_text()
        
        # Country patterns
        countries = [
            'United States', 'USA', 'Canada', 'United Kingdom', 'UK', 'Australia', 
            'Germany', 'France', 'Japan', 'China', 'India', 'Brazil', 'Mexico',
            'Netherlands', 'Sweden', 'Norway', 'Denmark', 'Finland', 'Switzerland',
            'Singapore', 'Malaysia', 'Thailand', 'Philippines', 'Indonesia',
            'South Korea', 'Taiwan', 'Hong Kong', 'New Zealand', 'South Africa',
            'Sri Lanka', 'Bangladesh', 'Pakistan', 'Nepal', 'Myanmar'
        ]
        
        found_countries = []
        for country in countries:
            if re.search(rf'\b{re.escape(country)}\b', text_content, re.IGNORECASE):
                found_countries.append(country)
        
        if found_countries:
            location_data['countries'] = list(set(found_countries))
        
        # Major cities
        major_cities = [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'San Francisco',
            'London', 'Manchester', 'Birmingham', 'Toronto', 'Vancouver',
            'Sydney', 'Melbourne', 'Berlin', 'Munich', 'Paris', 'Lyon',
            'Tokyo', 'Osaka', 'Beijing', 'Shanghai', 'Mumbai', 'Delhi',
            'Singapore', 'Kuala Lumpur', 'Bangkok', 'Manila', 'Jakarta',
            'Seoul', 'Taipei', 'Hong Kong', 'Dubai', 'Istanbul',
            'Colombo', 'Kandy', 'Dhaka', 'Karachi', 'Kathmandu'
        ]
        
        found_cities = []
        for city in major_cities:
            if re.search(rf'\b{re.escape(city)}\b', text_content, re.IGNORECASE):
                found_cities.append(city)
        
        if found_cities:
            location_data['cities'] = list(set(found_cities))
        
        return location_data

    def _extract_technology_mentions(self, soup: BeautifulSoup) -> List[str]:
        """Extract technology stack mentions"""
        text_content = soup.get_text().lower()
        
        # Technology keywords
        technologies = {
            'python', 'javascript', 'java', 'c#', 'php', 'ruby', 'go', 'typescript',
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
            'mysql', 'postgresql', 'mongodb', 'redis', 'aws', 'azure', 'docker',
            'kubernetes', 'tensorflow', 'pytorch', 'machine learning', 'ai',
            'blockchain', 'microservices', 'rest api', 'graphql'
        }
        
        found_technologies = []
        for tech in technologies:
            if tech in text_content:
                found_technologies.append(tech)
        
        return list(set(found_technologies))

    def _extract_people_entities(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract people and their roles using NER patterns"""
        text_content = soup.get_text()
        people = []
        
        # Common title patterns
        title_patterns = [
            r'(CEO|Chief Executive Officer|President|Founder|Co-Founder)\s*:?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(CTO|Chief Technology Officer|Tech Lead)\s*:?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(CFO|Chief Financial Officer)\s*:?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(Director|Manager|VP)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text_content)
            for match in matches:
                if len(match) == 2:
                    title, name = match
                    people.append({
                        'name': name.strip(),
                        'role': title.strip()
                    })
        
        return people

    def _extract_navigation_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract navigation structure"""
        nav_data = {}
        
        # Main navigation
        nav_elements = soup.find_all(['nav', 'ul'], class_=re.compile(r'nav|menu', re.I))
        main_nav_items = []
        
        for nav in nav_elements:
            links = nav.find_all('a', href=True)
            for link in links:
                text = link.get_text().strip()
                if text and len(text) < 50:
                    main_nav_items.append({
                        'text': text,
                        'href': link['href']
                    })
        
        if main_nav_items:
            nav_data['main_navigation'] = main_nav_items
        
        return nav_data

    def _extract_structured_html_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured HTML content"""
        structured_content = {}
        
        # Headers hierarchy
        headers = {}
        for i in range(1, 7):
            header_elements = soup.find_all(f'h{i}')
            if header_elements:
                headers[f'h{i}'] = [h.get_text().strip() for h in header_elements]
        
        if headers:
            structured_content['headers'] = headers
        
        return structured_content

# Maintain backwards compatibility
ScrapingService = EnhancedScrapingService
