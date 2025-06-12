"""
Enhanced Profile Generator Service

This service provides AI-powered company profile generation with advanced
natural language processing and machine learning capabilities.
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import AI and ML libraries
try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

try:
    import spacy
    from spacy import displacy
except ImportError:
    spacy = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    from langchain.memory import ConversationSummaryBufferMemory
    from langchain.llms import OpenAI as LangChainOpenAI
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
except ImportError:
    ConversationSummaryBufferMemory = None
    LangChainOpenAI = None
    LLMChain = None
    PromptTemplate = None

# Import local services
from app.services.data.scraping_service import EnhancedScrapingService

logger = logging.getLogger(__name__)

class EnhancedProfileGenerator:
    """Enhanced AI-powered company profile generator"""
    
    def __init__(self):
        """Initialize the enhanced profile generator"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Enhanced Profile Generator")
        
        # Initialize AI components
        self._initialize_ai_components()
        self._initialize_nlp_components()
        self._initialize_prompt_templates()
        
        # Initialize scraping service
        try:
            self.scraping_service = EnhancedScrapingService()
        except Exception as e:
            self.logger.warning(f"Failed to initialize scraping service: {e}")
            self.scraping_service = None
    
    def _initialize_ai_components(self):
        """Initialize AI and OpenAI components"""
        try:
            if OpenAI:
                self.openai_client = OpenAI()
                self.llm = LangChainOpenAI(temperature=0.7) if LangChainOpenAI else None
                self.memory = ConversationSummaryBufferMemory(
                    llm=self.llm,
                    max_token_limit=2000,
                    return_messages=True
                ) if ConversationSummaryBufferMemory and self.llm else None
            else:
                self.openai_client = None
                self.llm = None
                self.memory = None
                self.logger.warning("OpenAI not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI components: {e}")
            self.openai_client = None
            self.llm = None
            self.memory = None
    
    def _initialize_nlp_components(self):
        """Initialize NLP components"""
        try:
            if spacy:
                self.nlp = spacy.load("en_core_web_sm")
            else:
                self.nlp = None
                self.logger.warning("spaCy not available")
                
            if SentenceTransformer:
                self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
                self.semantic_model = SentenceTransformer('all-mpnet-base-v2')
            else:
                self.sentence_transformer = None
                self.semantic_model = None
                self.logger.warning("SentenceTransformers not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize NLP components: {e}")
            self.nlp = None
            self.sentence_transformer = None
            self.semantic_model = None
    
    def _initialize_prompt_templates(self):
        """Initialize prompt templates for AI generation"""
        self.prompt_templates = {
            "entity_extraction": """
You are an expert NLP entity extraction system. Extract comprehensive company information from the following HTML/text content and return ONLY valid JSON.

Text: {text}

ADVANCED EXTRACTION INSTRUCTIONS:
1. **Contact Information**: Look for phone numbers (any format), email addresses, contact forms, social media links
2. **Location Data**: Extract addresses, cities, countries, postal codes, geographic references, office locations
3. **Logo & Branding**: Find logo URLs, brand assets, company imagery
4. **Company Details**: Names, taglines, descriptions, about us content
5. **Services/Products**: All offerings, service descriptions, product catalogs
6. **People**: Names with titles, leadership team, staff information
7. **Technology**: Programming languages, frameworks, tools, platforms mentioned
8. **Business Info**: Industry, founding dates, company size, revenue, funding
9. **Social Proof**: Client names, testimonials, case studies, partnerships
10. **Navigation & Structure**: Menu items, page titles, section headers for context

EXTRACTION PATTERNS TO LOOK FOR:
- Phone: +XX XXX XXX XXXX, (XXX) XXX-XXXX, XXX.XXX.XXXX
- Email: name@domain.com, contact@, info@, hello@, support@
- Addresses: Street, City, State/Province, Country, Postal Code
- URLs: website links, social media profiles, career pages
- Logo: <img> tags with logo, brand, company name in src/alt
- People: CEO, CTO, Founder, Director, Manager + names
- Tech: React, Python, JavaScript, AWS, Docker, etc.

Return a JSON object with these fields:
{{
  "company_name": "extracted company name from title, headers, or branding",
  "logo_url": "direct URL to company logo image",
  "industry": "detailed industry classification", 
  "founded": "founding year or establishment date",
  "tagline": "company tagline or slogan",
  "description": "comprehensive company description from about/home sections",
  "contact_info": {{
    "phones": ["list of phone numbers found"],
    "emails": ["list of email addresses found"],
    "website": "main website URL",
    "social_media": [
      {{"platform": "linkedin/twitter/facebook", "url": "profile URL", "handle": "@username"}}
    ]
  }},
  "locations": [
    {{
      "type": "headquarters/office/branch",
      "address": "full street address",
      "city": "city name",
      "state": "state/province",
      "country": "country name",
      "postal_code": "postal/zip code",
      "coordinates": {{"lat": 0.0, "lng": 0.0}}
    }}
  ],
  "key_people": [
    {{"name": "person name", "role": "position/title", "description": "brief background", "linkedin": "linkedin URL if found"}}
  ],
  "products_services": [
    {{"name": "service/product name", "description": "detailed description", "category": "service category", "features": ["key features"]}}
  ],
  "technology_stack": ["comprehensive list of technologies, frameworks, tools, platforms mentioned"],
  "business_info": {{
    "company_size": "number of employees or size range",
    "revenue": "revenue information if available",
    "funding": "funding details if available",
    "established": "founding date or years in business"
  }},
  "mission_vision": "company mission and vision statements",
  "values": ["list of company values and principles"],
  "achievements": ["recent achievements, awards, recognitions, certifications"],
  "clients": ["notable clients or client types mentioned"],
  "partnerships": ["key partnerships and collaborations"],
  "global_presence": ["list of countries/regions where company operates"],
  "certifications": ["professional certifications, ISO standards, etc."],
  "languages": ["languages supported or spoken"],
  "specializations": ["areas of expertise or specialization"]
}}

IMPORTANT: Extract actual data found in the content. If information is not available, use empty string or empty array. Be thorough and look for information in headers, footers, navigation, content sections, and metadata.
""",
            
            "profile_synthesis": """
Create a comprehensive company profile using the following structured data:

Extracted Data: {extracted_data}
Custom Instructions: {custom_instructions}
Focus Areas: {focus_areas}

Synthesize all available information into a professional company profile. Use the extracted data to create detailed, informative content for each section.

Return ONLY valid JSON in this EXACT flat structure:
{{
  "company_name": "company name from extracted data",
  "company_overview": "comprehensive overview including mission, vision, values, company culture, and business focus. Include founding information, company size, and overall business approach.",
  "products_services": "detailed description of all products and services offered. Include service categories, descriptions, and unique value propositions. Format as comprehensive text covering all offerings.",
  "leadership_team": "detailed information about key leadership team members, their roles, backgrounds, and expertise. Include management structure and key personnel.",
  "market_position": "company's position in the market, competitive advantages, target markets, client base, and industry standing. Include partnerships and collaborations.",
  "recent_developments": "recent achievements, awards, recognitions, news, growth metrics, and notable developments. Include any significant milestones or expansions.",
  "technology_stack": ["comprehensive", "list", "of", "all", "technologies", "frameworks", "tools", "platforms", "programming languages", "mentioned"],
  "industry": "detailed industry classification and business sectors",
  "founded": "founding year or establishment date",
  "headquarters": "headquarters location and any additional office locations",
  "website": "company website URL if available",
  "company_size": "team size and organizational structure",
  "core_values": "company values and principles",
  "mission_statement": "company mission and vision statements"
}}

Instructions:
- Use ALL available data from the extraction
- Create comprehensive, professional descriptions
- Ensure each field contains substantial, meaningful content
- Do NOT nest the data under a "Company Profile" key
- If specific information is not available, provide relevant context or indicate "Not specified"
""",
            
            "content_enhancement": """
Polish and enhance the following company profile to create a professional, comprehensive business profile:

Current Profile: {current_profile}
Focus Areas: {focus_areas}

Enhancement Requirements:
- Improve readability and professional tone
- Add industry insights and context where appropriate
- Ensure consistency across all sections
- Highlight unique value propositions and differentiators
- Expand on key strengths and capabilities
- Provide actionable business intelligence

Return ONLY valid JSON in this EXACT flat structure:
{{
  "company_name": "polished company name",
  "company_overview": "enhanced comprehensive overview with improved flow, professional language, and strategic insights. Include company positioning, core business model, and key differentiators.",
  "products_services": "enhanced detailed description of all products and services with clear value propositions, target markets, and competitive advantages. Organize by service categories if applicable.",
  "leadership_team": "enhanced leadership information with professional backgrounds, expertise areas, and strategic roles. Include organizational structure and key decision makers.",
  "market_position": "enhanced market analysis including competitive positioning, target markets, industry standing, strategic partnerships, and growth opportunities.",
  "recent_developments": "enhanced recent achievements, milestones, awards, expansions, and strategic initiatives. Include growth metrics and future outlook where available.",
  "technology_stack": ["comprehensive", "enhanced", "technology", "list", "including", "frameworks", "tools", "platforms", "languages"],
  "industry": "enhanced industry classification with sector details",
  "founded": "founding information with historical context",
  "headquarters": "enhanced location information including geographic presence",
  "website": "company website URL",
  "company_size": "team size and organizational scale",
  "core_values": "company values and cultural principles",
  "mission_statement": "refined mission and vision statements",
  "competitive_advantages": "key differentiators and unique strengths",
  "target_markets": "primary target markets and customer segments"
}}

Quality Standards:
1. Use the FLAT structure above (no nested keys)
2. Ensure each field contains substantial, meaningful content
3. Maintain professional business language throughout
4. Provide specific, actionable insights
5. Highlight what makes this company unique
6. Ensure factual accuracy while enhancing presentation

Return ONLY the JSON structure above.
"""
        }
    
    async def generate_comprehensive_profile(
        self,
        urls: List[str] = None,
        documents: List[str] = None,
        custom_text: str = "",
        custom_instructions: str = "",
        focus_areas: List[str] = None,
        use_cache: bool = True,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """Generate a comprehensive company profile"""
        
        start_time = datetime.now()
        self.logger.info(f"Starting comprehensive profile generation for {len(urls or [])} URLs")
        
        try:
            # Step 1: Collect and process content
            processed_content = await self._collect_and_process_content(urls or [], custom_text)
            
            # Add documents to processed content
            if documents:
                for i, doc in enumerate(documents):
                    processed_content["total_content"] += f"\n\nDocument {i+1}:\n{doc}"
                    processed_content["sources"].append(f"document_{i+1}")
            
            # Step 2: Extract entities and structured data
            structured_data = await self._extract_entities_and_data(processed_content)
            
            # Step 3: Synthesize profile data
            enhanced_profile = await self._synthesize_profile_data(
                structured_data, custom_instructions, focus_areas
            )
            
            # Step 4: Generate final profile
            final_profile = await self._generate_final_profile(enhanced_profile, custom_instructions)
            
            # Calculate metadata
            generation_time = (datetime.now() - start_time).total_seconds()
            confidence_score = self._calculate_confidence_score(final_profile)
            
            return {
                "success": True,
                "profile": final_profile,
                "metadata": {
                    "generation_time": generation_time,
                    "sources_processed": len(processed_content.get("sources", [])),
                    "confidence_score": confidence_score,
                    "generation_method": "ai_enhanced",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Profile generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "profile": self._generate_fallback_profile(),
                "metadata": {
                    "generation_time": (datetime.now() - start_time).total_seconds(),
                    "sources_processed": len(urls or []),
                    "confidence_score": 0.5,
                    "generation_method": "fallback",
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    async def _collect_and_process_content(
        self, urls: List[str], custom_text: str
    ) -> Dict[str, Any]:
        """Collect and process content from URLs and custom text"""
        
        processed_content = {
            "scraped_data": {},
            "custom_text": custom_text,
            "total_content": "",
            "sources": []
        }
        
        # Process URLs if scraping service is available
        if self.scraping_service and urls:
            for url in urls:
                try:
                    scraped_data, metadata = self.scraping_service.scrape_website_enhanced(url)
                    processed_content["scraped_data"][url] = {
                        "data": scraped_data,
                        "metadata": metadata
                    }
                    processed_content["sources"].append(url)
                    
                    # Add to total content
                    if scraped_data:
                        content_text = json.dumps(scraped_data, indent=2)
                        processed_content["total_content"] += f"\n\nSource: {url}\n{content_text}"
                        
                except Exception as e:
                    self.logger.error(f"Failed to scrape {url}: {e}")
        
        # Add custom text
        if custom_text:
            processed_content["total_content"] += f"\n\nCustom Text:\n{custom_text}"
            processed_content["sources"].append("custom_text")
        
        return processed_content
    
    async def _extract_entities_and_data(
        self, processed_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract entities and structured data from processed content"""
        
        structured_data = {
            "entities": [],
            "company_info": {},
            "themes": [],
            "confidence": 0.5
        }
        
        content_text = processed_content.get("total_content", "")
        
        # Use NLP for entity extraction if available
        if self.nlp and content_text:
            try:
                doc = self.nlp(content_text[:1000000])  # Limit text size
                entities = []
                
                for ent in doc.ents:
                    if ent.label_ in ["ORG", "PERSON", "GPE", "PRODUCT", "MONEY"]:
                        entities.append({
                            "text": ent.text,
                            "label": ent.label_,
                            "confidence": 0.8
                        })
                
                structured_data["entities"] = entities[:15]  # Limit entities
                
            except Exception as e:
                self.logger.error(f"NLP entity extraction failed: {e}")
        
        # Use AI for structured extraction if available
        if self.openai_client and content_text:
            try:
                structured_data["company_info"] = await self._ai_extract_company_info(content_text)
            except Exception as e:
                self.logger.error(f"AI extraction failed: {e}")
        
        return structured_data
    
    async def _ai_extract_company_info(self, text: str) -> Dict[str, Any]:
        """Use AI to extract structured company information"""
        
        if not self.openai_client:
            return {}
        
        try:
            prompt = self.prompt_templates["entity_extraction"].format(text=text[:4000])
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert business analyst specializing in comprehensive company data extraction. Extract detailed, accurate information and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            self.logger.info(f"AI extraction response: {content[:500]}...")
            
            # Extract JSON from response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content.strip()
            
            self.logger.info(f"Extracted JSON content: {json_content[:300]}...")
            result = json.loads(json_content)
            self.logger.info(f"Successfully parsed AI extraction result")
            return result
            
        except Exception as e:
            self.logger.error(f"AI extraction error: {e}")
            if 'content' in locals():
                self.logger.error(f"Raw response content: {content}")
            return {}
    
    async def _synthesize_profile_data(
        self,
        structured_data: Dict[str, Any],
        custom_instructions: str = "",
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """Synthesize processed content into structured profile data"""
        
        if not self.openai_client:
            return self._generate_fallback_profile()
        
        try:
            prompt = self.prompt_templates["profile_synthesis"].format(
                extracted_data=json.dumps(structured_data, indent=2),
                custom_instructions=custom_instructions or "Generate a comprehensive professional company profile",
                focus_areas=", ".join(focus_areas or ["overview", "products", "leadership"])
            )
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a senior business analyst creating comprehensive company profiles for enterprise clients. Generate detailed, professional profiles with substantial content for each section. Return structured JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            self.logger.info(f"Profile synthesis response: {content[:500]}...")
            
            # Extract and parse JSON
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content.strip()
            
            self.logger.info(f"Profile synthesis JSON content: {json_content[:300]}...")
            result = json.loads(json_content)
            self.logger.info(f"Successfully parsed profile synthesis result")
            return result
            
        except Exception as e:
            self.logger.error(f"Profile synthesis error: {e}")
            if 'content' in locals():
                self.logger.error(f"Raw synthesis response: {content}")
            return self._generate_fallback_profile()
    
    async def _generate_final_profile(
        self,
        enhanced_profile: Dict[str, Any],
        custom_instructions: str = ""
    ) -> Dict[str, Any]:
        """Generate the final structured profile"""
        
        if not enhanced_profile or not self.openai_client:
            return self._generate_fallback_profile()
        
        try:
            # Use AI to enhance and polish the profile
            prompt = self.prompt_templates["content_enhancement"].format(
                current_profile=json.dumps(enhanced_profile, indent=2),
                focus_areas=custom_instructions or "Create a comprehensive, professional company profile"
            )
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert business intelligence writer creating premium company profiles for executive decision-making. Generate comprehensive, polished profiles with rich detail and professional insights. Return structured JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            self.logger.info(f"Final profile response: {content[:500]}...")
            
            # Extract and parse JSON
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content.strip()
            
            self.logger.info(f"Final profile JSON content: {json_content[:300]}...")
            final_profile = json.loads(json_content)
            self.logger.info(f"Successfully parsed final profile result")
            return final_profile
            
        except Exception as e:
            self.logger.error(f"Final profile generation failed: {e}")
            if 'content' in locals():
                self.logger.error(f"Raw final profile response: {content}")
            return enhanced_profile or self._generate_fallback_profile()
    
    def _generate_fallback_profile(self) -> Dict[str, Any]:
        """Generate a fallback profile when AI processing fails"""
        
        return {
            "company_name": "Generated Company",
            "company_overview": "This is a fallback profile generated when AI processing is unavailable. The company profile generation system is designed to provide comprehensive business intelligence and analysis.",
            "products_services": "Professional services and technology solutions",
            "leadership_team": "Experienced leadership team with industry expertise",
            "market_position": "Established player in the market with growth potential",
            "recent_developments": "Continuing to expand operations and improve service offerings",
            "technology_stack": ["Modern web technologies", "Cloud infrastructure", "AI/ML capabilities"],
            "full_profile": "This is a comprehensive fallback profile that demonstrates the system's capability to generate structured company information even when advanced AI processing is not available."
        }
    
    def _calculate_confidence_score(self, profile: Dict[str, Any]) -> float:
        """Calculate confidence score for the generated profile"""
        
        if not profile:
            return 0.0
        
        # Simple scoring based on content completeness
        score = 0.0
        fields = ["company_name", "company_overview", "products_services", "leadership_team"]
        
        for field in fields:
            if field in profile and profile[field]:
                score += 0.25
        
        return min(score, 1.0) 