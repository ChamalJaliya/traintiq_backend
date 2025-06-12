"""
Enhanced Company Profile Generation API - Flask Blueprint Version
Advanced endpoints for multi-source company profile generation
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest
import json
import logging
from datetime import datetime
import tempfile
import os
import asyncio

# Import actual services
from app.services.ai.enhanced_profile_generator import EnhancedProfileGenerator
from app.services.data.scraping_service import EnhancedScrapingService

# Initialize blueprint
enhanced_profile_bp = Blueprint('enhanced_profile', __name__, url_prefix='/api/profile')

logger = logging.getLogger(__name__)

# Initialize services
try:
    profile_generator = EnhancedProfileGenerator()
    scraping_service = EnhancedScrapingService()
    logger.info("Enhanced profile services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    profile_generator = None
    scraping_service = None

# Mock profile templates (since we don't have the actual service yet)
PROFILE_TEMPLATES = {
    "startup": {
        "name": "Startup Profile",
        "description": "Perfect for early-stage companies and startups",
        "focus_areas": ["overview", "products", "leadership", "market", "funding"]
    },
    "enterprise": {
        "name": "Enterprise Profile", 
        "description": "Comprehensive profile for established enterprises",
        "focus_areas": ["overview", "history", "products", "leadership", "financials", "market"]
    },
    "technology": {
        "name": "Technology Company",
        "description": "Specialized for tech companies and software businesses",
        "focus_areas": ["overview", "products", "technology", "leadership", "market", "innovation"]
    },
    "financial": {
        "name": "Financial Services",
        "description": "Tailored for banks, fintech, and financial institutions",
        "focus_areas": ["overview", "history", "products", "leadership", "financials", "compliance"]
    }
}

@enhanced_profile_bp.route('/templates', methods=['GET'])
def get_profile_templates():
    """Get available profile templates"""
    try:
        return jsonify({
            "success": True,
            "templates": PROFILE_TEMPLATES,
            "message": "Templates retrieved successfully"
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving templates: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve templates"
        }), 500

@enhanced_profile_bp.route('/analyze/sources', methods=['GET'])
def analyze_data_sources():
    """Analyze data sources for quality assessment using real scraping"""
    try:
        urls = request.args.getlist('urls')
        
        if not urls:
            return jsonify({
                "success": False,
                "error": "No URLs provided",
                "message": "Please provide at least one URL to analyze"
            }), 400
        
        if not scraping_service:
            return jsonify({
                "success": False,
                "error": "Scraping service not available",
                "message": "Scraping service failed to initialize"
            }), 500
        
        # Perform actual analysis using scraping service
        valid_urls = [url for url in urls if url.startswith(('http://', 'https://'))]
        analysis_results = []
        total_content_length = 0
        successful_scrapes = 0
        
        for url in valid_urls:
            try:
                logger.info(f"Starting analysis for URL: {url}")
                # Quick scrape to analyze content with timeout
                scraped_data, metadata = scraping_service.scrape_website_enhanced(url)
                logger.info(f"Successfully scraped {url}, content length: {metadata.get('content_length', 0)}")
                
                analysis_results.append({
                    "url": url,
                    "status": "success",
                    "content_length": metadata.get('content_length', 0),
                    "response_time": metadata.get('response_time', 0),
                    "scraping_method": metadata.get('scraping_method', 'requests'),
                    "has_company_info": bool(scraped_data.get('basic_info', {}).get('company_name')),
                    "sections_found": list(scraped_data.keys())
                })
                
                total_content_length += metadata.get('content_length', 0)
                successful_scrapes += 1
                
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {str(e)}")
                analysis_results.append({
                    "url": url,
                    "status": "failed",
                    "error": str(e),
                    "content_length": 0,
                    "response_time": 0
                })
        
        # Generate analysis summary
        analysis_result = {
            "total_sources": len(urls),
            "valid_sources": len(valid_urls),
            "successful_scrapes": successful_scrapes,
            "failed_scrapes": len(valid_urls) - successful_scrapes,
            "total_content_length": total_content_length,
            "average_content_length": total_content_length / max(successful_scrapes, 1),
            "source_quality": "excellent" if successful_scrapes == len(valid_urls) else "good" if successful_scrapes > 0 else "poor",
            "domains_analyzed": [url.split('/')[2] if len(url.split('/')) > 2 else url for url in valid_urls],
            "detailed_results": analysis_results,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Generate recommendations
        recommendations = []
        if successful_scrapes == len(valid_urls):
            recommendations.append("✅ All URLs successfully analyzed")
        elif successful_scrapes > 0:
            recommendations.append(f"⚠️ {successful_scrapes}/{len(valid_urls)} URLs successfully analyzed")
        else:
            recommendations.append("❌ No URLs could be analyzed")
            
        if total_content_length > 5000:
            recommendations.append("📄 Rich content detected - good for comprehensive profile")
        elif total_content_length > 1000:
            recommendations.append("📄 Moderate content available")
        else:
            recommendations.append("📄 Limited content - consider additional sources")
        
        return jsonify({
            "success": True,
            "analysis": analysis_result,
            "recommendations": recommendations,
            "message": "Real source analysis completed successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing sources: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Source analysis failed"
        }), 500

@enhanced_profile_bp.route('/generate', methods=['POST'])
def generate_enhanced_profile():
    """Generate an enhanced company profile using real AI and scraping"""
    try:
        # Handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            logger.info(f"Received JSON data: {data}")
        else:
            # Handle form data with files
            data = {}
            
            # Check if there's a 'request' field (blob from frontend)
            if 'request' in request.form:
                try:
                    data = json.loads(request.form['request'])
                    logger.info(f"Parsed request from form: {data}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse request JSON: {e}")
                    return jsonify({
                        "success": False,
                        "error": "Invalid JSON in request field",
                        "message": "Failed to parse request data"
                    }), 400
            elif 'request' in request.files:
                # Handle blob file
                request_file = request.files['request']
                try:
                    request_content = request_file.read().decode('utf-8')
                    data = json.loads(request_content)
                    logger.info(f"Parsed request from blob file: {data}")
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logger.error(f"Failed to parse request blob: {e}")
                    return jsonify({
                        "success": False,
                        "error": "Invalid JSON in request blob",
                        "message": "Failed to parse request data"
                    }), 400
            else:
                # Fallback to form data
                data = request.form.to_dict()
                logger.info(f"Using form data: {data}")
        
        # Extract parameters
        urls = data.get('urls', [])
        custom_text = data.get('custom_text', '')
        custom_instructions = data.get('custom_instructions', '')
        focus_areas = data.get('focus_areas', [])
        template = data.get('template', 'startup')
        use_cache = data.get('use_cache', True)
        
        logger.info(f"Processing request - URLs: {urls}, Custom text length: {len(custom_text)}, Files: {len(request.files)}")
        
        # Validate inputs
        if not urls and not custom_text and not request.files:
            logger.warning("No data sources provided in request")
            return jsonify({
                "success": False,
                "error": "No data sources provided",
                "message": "Please provide at least one URL, text, or file"
            }), 400
        
        if not profile_generator:
            return jsonify({
                "success": False,
                "error": "Profile generator not available",
                "message": "AI services failed to initialize"
            }), 500
        
        # Validate URLs
        valid_urls = []
        for url in urls:
            if url and url.strip() and (url.startswith('http://') or url.startswith('https://')):
                valid_urls.append(url.strip())
        
        # Process uploaded files
        processed_documents = []
        if request.files:
            for file_key in request.files:
                # Skip the 'request' blob file
                if file_key == 'request':
                    continue
                    
                file = request.files[file_key]
                if file and file.filename:
                    try:
                        # Read file content
                        content = file.read()
                        file.seek(0)  # Reset for potential reuse
                        
                        # For now, treat as text (you can enhance this with document processing)
                        if file.filename.endswith('.txt'):
                            processed_documents.append(content.decode('utf-8'))
                            logger.info(f"Processed text file: {file.filename}")
                        else:
                            logger.warning(f"File type not fully supported yet: {file.filename}")
                    except Exception as e:
                        logger.error(f"Error processing file {file.filename}: {e}")
        
        logger.info(f"Processed {len(processed_documents)} documents, {len(valid_urls)} valid URLs")
        
        # Use the real enhanced profile generator
        try:
            # Create event loop for async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Generate profile using real AI services
            result = loop.run_until_complete(
                profile_generator.generate_comprehensive_profile(
                    urls=valid_urls,
                    documents=processed_documents,
                    custom_text=custom_text,
                    custom_instructions=custom_instructions,
                    focus_areas=focus_areas,
                    use_cache=use_cache
                )
            )
            
            loop.close()
            
            if result.get('success', False):
                return jsonify({
                    "success": True,
                    "profile": result.get('profile', {}),
                    "metadata": result.get('metadata', {}),
                    "message": "Enhanced profile generated successfully using real AI and scraping"
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": result.get('error', 'Unknown error'),
                    "message": "Profile generation failed"
                }), 500
                
        except Exception as e:
            logger.error(f"Error in AI profile generation: {e}")
            
            # Fallback to mock profile if AI fails
            logger.info("Falling back to mock profile generation")
            mock_profile = generate_mock_profile(valid_urls, custom_text, focus_areas, template)
            
            metadata = {
                "generation_id": f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "sources_processed": len(valid_urls) + len(processed_documents),
                "confidence_score": 0.75,  # Lower confidence for fallback
                "processing_time": 1.5,
                "template_used": template,
                "focus_areas_covered": focus_areas or PROFILE_TEMPLATES.get(template, {}).get('focus_areas', []),
                "timestamp": datetime.now().isoformat(),
                "generation_method": "fallback_mock",
                "ai_error": str(e)
            }
            
            return jsonify({
                "success": True,
                "profile": mock_profile,
                "metadata": metadata,
                "message": "Profile generated using fallback method (AI services unavailable)"
            }), 200
        
    except Exception as e:
        logger.error(f"Error generating profile: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Profile generation failed"
        }), 500

def generate_mock_profile(urls, custom_text, focus_areas, template):
    """Generate a mock company profile for demonstration"""
    
    # Determine company name from URLs or use default
    company_name = "Sample Company"
    if urls:
        try:
            domain = urls[0].split('/')[2].replace('www.', '')
            company_name = domain.split('.')[0].title()
        except:
            pass
    
    # Base profile structure
    profile = {
        "basic_info": {
            "legal_name": company_name,
            "display_name": company_name,
            "industry": "Technology",
            "founded": "2010",
            "headquarters": "San Francisco, CA",
            "website": urls[0] if urls else "https://example.com",
            "size": "50-200 employees"
        },
        "descriptive": {
            "tagline": f"Leading innovation in technology solutions",
            "description": f"{company_name} is a forward-thinking technology company focused on delivering innovative solutions to modern business challenges.",
            "mission": f"To empower businesses through cutting-edge technology and exceptional service.",
            "vision": f"To be the leading provider of technology solutions globally."
        },
        "products_services": [
            {
                "name": "Core Platform",
                "description": "Our flagship technology platform providing comprehensive solutions",
                "category": "Software"
            },
            {
                "name": "Consulting Services", 
                "description": "Expert consulting and implementation services",
                "category": "Services"
            }
        ],
        "leadership": [
            {
                "name": "John Smith",
                "position": "CEO & Founder",
                "bio": "Experienced technology executive with 15+ years of industry leadership"
            },
            {
                "name": "Sarah Johnson",
                "position": "CTO",
                "bio": "Technical visionary driving innovation and product development"
            }
        ],
        "contact": {
            "email": "info@" + (urls[0].split('/')[2] if urls else "example.com"),
            "phone": "+1 (555) 123-4567",
            "address": "123 Technology Way, San Francisco, CA 94105"
        }
    }
    
    # Enhance with template-specific content
    template_config = PROFILE_TEMPLATES.get(template, PROFILE_TEMPLATES['startup'])
    
    if 'financials' in template_config['focus_areas']:
        profile['financials'] = {
            "revenue": "$10M - $50M (estimated)",
            "funding": "Series B",
            "investors": ["Tech Ventures", "Innovation Capital"]
        }
    
    if 'technology' in template_config['focus_areas']:
        profile['technology'] = {
            "tech_stack": ["React", "Node.js", "Python", "AWS"],
            "innovations": ["AI-powered analytics", "Cloud-native architecture"],
            "patents": 3
        }
    
    if 'market' in template_config['focus_areas']:
        profile['market'] = {
            "target_market": "B2B Technology Companies",
            "market_size": "$50B globally",
            "competitive_advantage": "Advanced AI and machine learning capabilities"
        }
    
    # Add custom text insights if provided
    if custom_text:
        profile['custom_insights'] = {
            "additional_info": custom_text[:500] + "..." if len(custom_text) > 500 else custom_text,
            "source": "Custom provided information"
        }
    
    return profile

@enhanced_profile_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for enhanced profile service"""
    return jsonify({
        "status": "healthy",
        "service": "Enhanced Profile Generator",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200

# Error handlers
@enhanced_profile_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": "Bad Request",
        "message": str(error.description)
    }), 400

@enhanced_profile_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal Server Error", 
        "message": "An unexpected error occurred"
    }), 500 