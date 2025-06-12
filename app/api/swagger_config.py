"""
Swagger/OpenAPI Configuration for TraintiQ Profile Generator API
Comprehensive API documentation with detailed schemas and examples
"""

from flask_restx import Api, Resource, fields, Namespace
from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api_docs', __name__)

# Initialize Flask-RESTx API with comprehensive configuration
api = Api(
    api_bp,
    version='2.0.0',
    title='TraintiQ Profile Generator API',
    description='''
    ## Advanced Company Profile Generation System
    
    This API provides comprehensive company profile generation capabilities using:
    - **AI-Powered Analysis**: OpenAI GPT-4 for intelligent content generation
    - **Multi-Source Data Extraction**: Web scraping, document processing, and structured data analysis
    - **Enhanced NLP/NER**: Advanced entity extraction and content categorization
    - **Real-time Processing**: Asynchronous profile generation with status tracking
    
    ### Key Features:
    - 🤖 **AI-Enhanced Profiles**: Intelligent content synthesis and enhancement
    - 🌐 **Multi-Source Scraping**: Website, social media, and document analysis
    - 📊 **Structured Data**: Organized sections for products, leadership, technology stack
    - 🎨 **Template System**: Customizable profile templates for different industries
    - 📈 **Analytics**: Comprehensive source analysis and quality assessment
    - 🔍 **Advanced Search**: Semantic search with vector embeddings
    
    ### Authentication:
    Currently using development mode. Production deployment will require API keys.
    
    ### Rate Limits:
    - Profile Generation: 10 requests/minute
    - Source Analysis: 20 requests/minute
    - Template Operations: 50 requests/minute
    ''',
    doc='/docs/',
    contact='TraintiQ Development Team',
    contact_email='dev@traintiq.com',
    license='MIT',
    license_url='https://opensource.org/licenses/MIT',
    authorizations={
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
            'description': 'API Key for authentication (future implementation)'
        }
    },
    security='apikey'
)

# Define comprehensive data models for Swagger documentation

# Basic response models
base_response = api.model('BaseResponse', {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'message': fields.String(required=True, description='Response message'),
    'timestamp': fields.DateTime(description='Response timestamp')
})

error_response = api.model('ErrorResponse', {
    'success': fields.Boolean(required=True, default=False, description='Always false for errors'),
    'error': fields.String(required=True, description='Error type or code'),
    'message': fields.String(required=True, description='Detailed error message'),
    'details': fields.Raw(description='Additional error details'),
    'timestamp': fields.DateTime(description='Error timestamp')
})

# Profile template models
profile_template = api.model('ProfileTemplate', {
    'name': fields.String(required=True, description='Template display name'),
    'description': fields.String(required=True, description='Template description and use case'),
    'focus_areas': fields.List(fields.String, required=True, description='Key areas this template focuses on')
})

templates_response = api.model('TemplatesResponse', {
    'success': fields.Boolean(required=True, default=True),
    'templates': fields.Raw(required=True, description='Available profile templates'),
    'message': fields.String(required=True, description='Success message')
})

# Source analysis models
source_analysis_detail = api.model('SourceAnalysisDetail', {
    'url': fields.String(required=True, description='Analyzed URL'),
    'status': fields.String(required=True, enum=['success', 'failed'], description='Analysis status'),
    'content_length': fields.Integer(description='Content length in characters'),
    'response_time': fields.Float(description='Response time in seconds'),
    'scraping_method': fields.String(description='Method used for scraping (requests/selenium)'),
    'has_company_info': fields.Boolean(description='Whether company information was found'),
    'sections_found': fields.List(fields.String, description='Data sections successfully extracted'),
    'error': fields.String(description='Error message if analysis failed')
})

source_analysis_summary = api.model('SourceAnalysisSummary', {
    'total_sources': fields.Integer(required=True, description='Total number of URLs provided'),
    'valid_sources': fields.Integer(required=True, description='Number of valid HTTP/HTTPS URLs'),
    'successful_scrapes': fields.Integer(required=True, description='Number of successfully analyzed URLs'),
    'failed_scrapes': fields.Integer(required=True, description='Number of failed analyses'),
    'total_content_length': fields.Integer(required=True, description='Total content length across all sources'),
    'average_content_length': fields.Float(required=True, description='Average content length per source'),
    'source_quality': fields.String(required=True, enum=['excellent', 'good', 'poor'], description='Overall source quality assessment'),
    'domains_analyzed': fields.List(fields.String, description='List of domains that were analyzed'),
    'detailed_results': fields.List(fields.Nested(source_analysis_detail), description='Detailed results for each URL'),
    'analysis_timestamp': fields.DateTime(required=True, description='When the analysis was performed')
})

source_analysis_response = api.model('SourceAnalysisResponse', {
    'success': fields.Boolean(required=True, default=True),
    'analysis': fields.Nested(source_analysis_summary, required=True, description='Comprehensive source analysis'),
    'recommendations': fields.List(fields.String, required=True, description='Actionable recommendations based on analysis'),
    'message': fields.String(required=True, description='Analysis completion message')
})

# Enhanced profile generation models
company_basic_info = api.model('CompanyBasicInfo', {
    'company_name': fields.String(required=True, description='Official company name'),
    'company_overview': fields.String(required=True, description='Comprehensive company overview'),
    'industry': fields.String(description='Primary industry sector'),
    'founded_year': fields.String(description='Year company was founded'),
    'headquarters': fields.String(description='Company headquarters location'),
    'company_size': fields.String(description='Number of employees or company size category'),
    'website': fields.String(description='Official company website'),
    'description': fields.String(description='Detailed company description')
})

product_service = api.model('ProductService', {
    'name': fields.String(required=True, description='Product or service name'),
    'description': fields.String(required=True, description='Detailed description'),
    'category': fields.String(description='Product/service category'),
    'features': fields.List(fields.String, description='Key features or capabilities')
})

leadership_member = api.model('LeadershipMember', {
    'name': fields.String(required=True, description='Full name'),
    'position': fields.String(required=True, description='Job title or position'),
    'bio': fields.String(description='Professional biography'),
    'experience': fields.String(description='Years of experience or background'),
    'linkedin': fields.String(description='LinkedIn profile URL'),
    'image': fields.String(description='Profile image URL')
})

technology_item = api.model('TechnologyItem', {
    'name': fields.String(required=True, description='Technology name'),
    'category': fields.String(required=True, description='Technology category (frontend, backend, database, etc.)'),
    'description': fields.String(description='How the technology is used'),
    'version': fields.String(description='Version or specification')
})

contact_info = api.model('ContactInfo', {
    'email': fields.String(description='Primary contact email'),
    'phone': fields.String(description='Primary contact phone'),
    'address': fields.String(description='Physical address'),
    'social_media': fields.Raw(description='Social media profiles and links')
})

enhanced_profile_data = api.model('EnhancedProfileData', {
    'basic_info': fields.Nested(company_basic_info, required=True, description='Basic company information'),
    'products_services': fields.List(fields.Nested(product_service), description='Products and services offered'),
    'leadership_team': fields.List(fields.Nested(leadership_member), description='Key leadership team members'),
    'technology_stack': fields.List(fields.Nested(technology_item), description='Technologies and tools used'),
    'contact_info': fields.Nested(contact_info, description='Contact information'),
    'company_values': fields.List(fields.String, description='Core company values and principles'),
    'achievements': fields.List(fields.String, description='Notable achievements and awards'),
    'market_position': fields.String(description='Market position and competitive advantages'),
    'recent_news': fields.List(fields.String, description='Recent news and updates'),
    'financial_info': fields.Raw(description='Financial information (if available)')
})

generation_metadata = api.model('GenerationMetadata', {
    'generation_time': fields.Float(required=True, description='Time taken to generate profile (seconds)'),
    'sources_processed': fields.Integer(required=True, description='Number of sources successfully processed'),
    'ai_model_used': fields.String(required=True, description='AI model used for generation'),
    'content_quality_score': fields.Float(description='Quality score of generated content (0-1)'),
    'data_sources': fields.List(fields.String, description='List of data sources used'),
    'processing_method': fields.String(description='Method used for processing (enhanced/standard)'),
    'tokens_used': fields.Integer(description='Number of AI tokens consumed'),
    'generation_timestamp': fields.DateTime(required=True, description='When the profile was generated')
})

enhanced_profile_response = api.model('EnhancedProfileResponse', {
    'success': fields.Boolean(required=True, default=True),
    'profile_data': fields.Nested(enhanced_profile_data, required=True, description='Complete generated profile'),
    'metadata': fields.Nested(generation_metadata, required=True, description='Generation metadata and statistics'),
    'message': fields.String(required=True, description='Generation completion message')
})

# Request models
profile_generation_request = api.model('ProfileGenerationRequest', {
    'urls': fields.List(fields.String, required=True, description='List of URLs to analyze (company website, social media, etc.)', 
                       example=['https://www.company.com', 'https://linkedin.com/company/example']),
    'custom_text': fields.String(description='Additional custom text or instructions for profile generation',
                                example='Focus on the company\'s AI and machine learning capabilities'),
    'focus_areas': fields.List(fields.String, description='Specific areas to focus on during generation',
                              example=['products', 'leadership', 'technology', 'market_position']),
    'template': fields.String(description='Profile template to use', enum=['startup', 'enterprise', 'technology', 'financial'],
                             example='technology'),
    'include_financial': fields.Boolean(default=False, description='Whether to include financial information'),
    'include_news': fields.Boolean(default=True, description='Whether to include recent news and updates'),
    'max_content_length': fields.Integer(default=5000, description='Maximum content length for generated sections'),
    'language': fields.String(default='en', description='Language for generated content', example='en')
})

# Health check model
health_response = api.model('HealthResponse', {
    'status': fields.String(required=True, enum=['healthy', 'degraded', 'unhealthy'], description='Service health status'),
    'timestamp': fields.DateTime(required=True, description='Health check timestamp'),
    'version': fields.String(required=True, description='API version'),
    'services': fields.Raw(required=True, description='Status of individual services'),
    'uptime': fields.Float(description='Service uptime in seconds'),
    'memory_usage': fields.Raw(description='Memory usage statistics'),
    'database_status': fields.String(description='Database connection status')
})

# Create namespaces for better organization
profile_ns = Namespace('profile', description='Enhanced Profile Generation Operations')
templates_ns = Namespace('templates', description='Profile Template Management')
analysis_ns = Namespace('analysis', description='Data Source Analysis')
health_ns = Namespace('health', description='System Health and Monitoring')

# Add namespaces to API
api.add_namespace(profile_ns, path='/api/profile')
api.add_namespace(templates_ns, path='/api/profile/templates')
api.add_namespace(analysis_ns, path='/api/profile/analyze')
api.add_namespace(health_ns, path='/api/profile/health')

# Export models for use in route files
__all__ = [
    'api', 'api_bp', 'profile_ns', 'templates_ns', 'analysis_ns', 'health_ns',
    'base_response', 'error_response', 'templates_response', 'source_analysis_response',
    'enhanced_profile_response', 'profile_generation_request', 'health_response'
] 