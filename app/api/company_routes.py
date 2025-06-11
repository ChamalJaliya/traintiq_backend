from flask import Blueprint
from flask_restx import Resource, Namespace, fields, Api
from app import db
from app.models.company import Company
from app.schemas.company_schema import CompanyProfileSchema
from app.api import api
from app.services.company_service import CompanyService
from app.dto.company_dto import (
    CreateCompanyDTO, UpdateCompanyDTO, ScrapeCompanyDTO,
    CompanyProfileResponseDTO, GeoLocation, SocialMediaProfile,
    FinancialYearData, FundingRound, KeyPerson, ProductService,
    BoardMember
)
from app.exceptions import (
    ValidationException,
    NotFoundException,
    DatabaseException,
    ExternalServiceException
)

# Import your services
from app.services.scraping_service import ScrapingService
from app.services.data_extraction_service import DataExtractionService
from app.services.profile_generation_service import ProfileGenerationService
import uuid
from datetime import datetime

# Create Blueprint and API namespace
company_bp = Blueprint('company_bp', __name__)
api = Namespace('company', description='Company operations')

# Initialize schemas
company_schema = CompanyProfileSchema()
companies_schema = CompanyProfileSchema(many=True)

# Initialize services
scraping_service = ScrapingService()
data_extraction_service = DataExtractionService()
profile_generation_service = ProfileGenerationService()
company_service = CompanyService()

# Define nested models for Swagger documentation
geo_location = api.model('GeoLocation', {
    'lat': fields.Float(required=True, description='Latitude', example=37.7749),
    'lng': fields.Float(required=True, description='Longitude', example=-122.4194),
    'address': fields.String(required=True, description='Full address', example='550 Market St, San Francisco, CA 94104, USA')
})

social_media_profile = api.model('SocialMediaProfile', {
    'platform': fields.String(required=True, description='Social media platform name', example='linkedin'),
    'url': fields.String(required=True, description='Profile URL', example='https://linkedin.com/company/nexuswave'),
    'followers': fields.Integer(description='Number of followers', example=12450)
})

financial_year_data = api.model('FinancialYearData', {
    'year': fields.Integer(required=True, description='Financial year', example=2023),
    'revenue': fields.Float(required=True, description='Annual revenue', example=48200000),
    'profit': fields.Float(required=True, description='Annual profit', example=7500000),
    'currency': fields.String(required=True, description='Currency code (e.g., USD)', example='USD')
})

funding_round = api.model('FundingRound', {
    'date': fields.DateTime(required=True, description='Funding round date', example='2021-03-15T00:00:00Z'),
    'roundType': fields.String(required=True, description='Type of funding round', example='Series B'),
    'amount': fields.Float(required=True, description='Funding amount', example=25000000),
    'investors': fields.List(fields.String, required=True, description='List of investors', example=['Sequoia Capital', 'Andreessen Horowitz']),
    'valuation': fields.Float(description='Company valuation at time of funding', example=180000000)
})

key_person = api.model('KeyPerson', {
    'name': fields.String(required=True, description='Person name', example='Dr. Samantha Chen'),
    'title': fields.String(required=True, description='Job title', example='CEO & Co-Founder'),
    'linkedinUrl': fields.String(description='LinkedIn profile URL', example='https://linkedin.com/in/samanthachen')
})

product_service = api.model('ProductService', {
    'name': fields.String(required=True, description='Product/service name', example='WaveSync Core'),
    'category': fields.String(required=True, description='Category', example='Data Integration Platform'),
    'description': fields.String(required=True, description='Description', example='Real-time data pipeline orchestration'),
    'tags': fields.List(fields.String, description='Tags', example=['enterprise', 'on-premise', 'cloud']),
    'launchDate': fields.DateTime(description='Launch date', example='2022-09-01T00:00:00Z')
})

board_member = api.model('BoardMember', {
    'name': fields.String(required=True, description='Board member name', example='Michael Johnson'),
    'title': fields.String(required=True, description='Board position/title', example='Board Chair (Sequoia Capital)')
})

# Define main section models
basic_info = api.model('BasicInfo', {
    'legalName': fields.String(required=True, description='Legal company name', example='NexusWave Technologies Inc.'),
    'tradingName': fields.String(description='Trading name', example='NexusWave'),
    'dba': fields.String(description='Doing Business As name', example='WaveTech'),
    'logoUrl': fields.String(description='URL to company logo', example='https://placehold.co/100x100/2196F3/ffffff?text=NW'),
    'foundedDate': fields.DateTime(description='Company founding date', example='2015-06-15T00:00:00Z'),
    'incorporationDate': fields.DateTime(description='Legal incorporation date', example='2015-05-01T00:00:00Z'),
    'companyType': fields.String(description='Type of company', example='private'),
    'industryCodes': fields.List(fields.String, description='Industry classification codes', example=['541511', '518210'])
})

operational = api.model('Operational', {
    'headquarters': fields.Nested(geo_location, description='Company headquarters'),
    'locations': fields.List(fields.Nested(geo_location), description='Other locations'),
    'employeeCount': fields.Integer(description='Number of employees', example=342),
    'employeeRange': fields.String(description='Employee count range', example='301-500'),
    'operatingCountries': fields.List(fields.String, description='Countries of operation', example=['US', 'CA', 'GB', 'DE']),
    'subsidiaries': fields.List(fields.String, description='Subsidiary companies', example=['WaveTech UK Ltd', 'NexusWave Analytics'])
})

contact = api.model('Contact', {
    'primaryPhone': fields.String(description='Primary contact number', example='+1-415-555-0199'),
    'tollFreePhone': fields.String(description='Toll-free number', example='+1-800-555-3482'),
    'email': fields.String(description='Primary email', example='info@nexuswave.example'),
    'investorEmail': fields.String(description='Investor relations email', example='investors@nexuswave.example'),
    'socialMedia': fields.List(fields.Nested(social_media_profile), description='Social media profiles')
})

financials = api.model('Financials', {
    'stockSymbol': fields.String(description='Stock market symbol', example='PRIVATE'),
    'financialData': fields.List(fields.Nested(financial_year_data), description='Annual financial data'),
    'fundingRounds': fields.List(fields.Nested(funding_round), description='Funding rounds')
})

descriptive = api.model('Descriptive', {
    'mission': fields.String(description='Company mission', example='Empower businesses through intelligent data orchestration'),
    'vision': fields.String(description='Company vision', example='To become the operating system for enterprise data flows'),
    'tagline': fields.String(description='Company tagline', example='The Data Fabric Company'),
    'description': fields.String(description='Company description', 
                               example='NexusWave provides next-generation data integration platforms that help enterprises unify, process, and analyze data across hybrid cloud environments.'),
    'coreValues': fields.List(fields.String, description='Core company values', 
                            example=['Innovation', 'Customer Obsession', 'Data Integrity', 'Collaboration']),
    'keywords': fields.List(fields.String, description='Keywords for categorization',
                          example=['data integration', 'ETL', 'cloud computing', 'big data'])
})

relationships = api.model('Relationships', {
    'keyPeople': fields.List(fields.Nested(key_person), description='Key personnel'),
    'productsServices': fields.List(fields.Nested(product_service), description='Products and services'),
    'clients': fields.List(fields.String, description='Major clients',
                         example=['Fortune 500 Retailer', 'Global Bank Corp', 'TechUniverse']),
    'partners': fields.List(fields.String, description='Business partners',
                          example=['AWS', 'Snowflake', 'Databricks']),
    'competitors': fields.List(fields.String, description='Main competitors',
                             example=['Informatica', 'Talend', 'Fivetran'])
})

governance = api.model('Governance', {
    'ceo': fields.Raw(description='CEO information', 
                     example={'name': 'Dr. Samantha Chen', 'title': 'Chief Executive Officer'}),
    'boardMembers': fields.List(fields.Nested(board_member), description='Board members'),
    'certifications': fields.List(fields.String, description='Company certifications',
                                example=['SOC 2 Type II', 'ISO 27001'])
})

digital_presence = api.model('DigitalPresence', {
    'websiteUrl': fields.String(description='Company website URL', example='https://nexuswave.example'),
    'careersUrl': fields.String(description='Careers page URL', example='https://nexuswave.example/careers'),
    'techStack': fields.List(fields.String, description='Technology stack',
                           example=['Angular', 'Node.js', 'Kubernetes', 'PostgreSQL']),
    'monthlyVisitors': fields.Integer(description='Monthly website visitors', example=125000)
})

scraped_data = api.model('ScrapedData', {
    'sources': fields.List(fields.String, description='Data source URLs',
                         example=['https://nexuswave.example/about',
                                'https://crunchbase.com/nexuswave']),
    'lastScraped': fields.DateTime(description='Last scraping timestamp',
                                 example='2023-11-15T14:30:00Z'),
    'confidenceScore': fields.Float(description='Data confidence score (0-1)',
                                  example=0.92)
})

metadata = api.model('Metadata', {
    'lastUpdated': fields.DateTime(description='Last update timestamp',
                                 example='2023-11-16T09:15:00Z'),
    'created': fields.DateTime(description='Creation timestamp',
                             example='2020-01-10T10:00:00Z'),
    'dataSources': fields.List(fields.String, description='Data source types',
                             example=['scraped', 'manual-entry'])
})

# Main company profile model
company_profile = api.model('CompanyProfile', {
    'id': fields.String(readonly=True, description='Company ID'),
    'basicInfo': fields.Nested(basic_info, required=True),
    'operational': fields.Nested(operational),
    'contact': fields.Nested(contact),
    'financials': fields.Nested(financials),
    'descriptive': fields.Nested(descriptive),
    'relationships': fields.Nested(relationships),
    'governance': fields.Nested(governance),
    'digitalPresence': fields.Nested(digital_presence),
    'scrapedData': fields.Nested(scraped_data),
    'metaInfo': fields.Nested(metadata),
    'customSections': fields.Raw(description='Custom key-value pairs')
})

# Example request data
example_request = {
    "basicInfo": {
        "legalName": "NexusWave Technologies Inc.",
        "tradingName": "NexusWave",
        "dba": "WaveTech",
        "logoUrl": "https://placehold.co/100x100/2196F3/ffffff?text=NW",
        "foundedDate": "2015-06-15T00:00:00Z",
        "incorporationDate": "2015-05-01T00:00:00Z",
        "companyType": "private",
        "industryCodes": ["541511", "518210"]
    },
    "operational": {
        "headquarters": {
            "lat": 37.7749,
            "lng": -122.4194,
            "address": "550 Market St, San Francisco, CA 94104, USA"
        },
        "locations": [
            {
                "lat": 40.7128,
                "lng": -74.0060,
                "address": "One Liberty Plaza, New York, NY 10006, USA"
            }
        ],
        "employeeCount": 342,
        "employeeRange": "301-500",
        "operatingCountries": ["US", "CA", "GB", "DE"],
        "subsidiaries": ["WaveTech UK Ltd", "NexusWave Analytics"]
    },
    "contact": {
        "primaryPhone": "+1-415-555-0199",
        "tollFreePhone": "+1-800-555-3482",
        "email": "info@nexuswave.example",
        "investorEmail": "investors@nexuswave.example",
        "socialMedia": [
            {
                "platform": "linkedin",
                "url": "https://linkedin.com/company/nexuswave",
                "followers": 12450
            },
            {
                "platform": "twitter",
                "url": "https://twitter.com/nexuswave",
                "followers": 8765
            }
        ]
    },
    "financials": {
        "stockSymbol": "PRIVATE",
        "financialData": [
            {
                "year": 2023,
                "revenue": 48200000,
                "profit": 7500000,
                "currency": "USD"
            },
            {
                "year": 2022,
                "revenue": 38500000,
                "profit": 5200000,
                "currency": "USD"
            }
        ],
        "fundingRounds": [
            {
                "date": "2021-03-15T00:00:00Z",
                "roundType": "Series B",
                "amount": 25000000,
                "investors": ["Sequoia Capital", "Andreessen Horowitz"],
                "valuation": 180000000
            }
        ]
    },
    "descriptive": {
        "mission": "Empower businesses through intelligent data orchestration",
        "vision": "To become the operating system for enterprise data flows",
        "tagline": "The Data Fabric Company",
        "description": "NexusWave provides next-generation data integration platforms that help enterprises unify, process, and analyze data across hybrid cloud environments. Our patented WaveSync technology enables real-time data synchronization at unprecedented scale.",
        "coreValues": ["Innovation", "Customer Obsession", "Data Integrity", "Collaboration"],
        "keywords": ["data integration", "ETL", "cloud computing", "big data"]
    },
    "relationships": {
        "keyPeople": [
            {
                "name": "Dr. Samantha Chen",
                "title": "CEO & Co-Founder",
                "linkedinUrl": "https://linkedin.com/in/samanthachen"
            },
            {
                "name": "Raj Patel",
                "title": "CTO",
                "linkedinUrl": "https://linkedin.com/in/rajpatelcto"
            }
        ],
        "productsServices": [
            {
                "name": "WaveSync Core",
                "category": "Data Integration Platform",
                "description": "Real-time data pipeline orchestration",
                "tags": ["enterprise", "on-premise", "cloud"]
            },
            {
                "name": "WaveFlow Cloud",
                "category": "SaaS Solution",
                "description": "Fully managed data integration service",
                "launchDate": "2022-09-01T00:00:00Z"
            }
        ],
        "clients": ["Fortune 500 Retailer", "Global Bank Corp", "TechUniverse"],
        "partners": ["AWS", "Snowflake", "Databricks"],
        "competitors": ["Informatica", "Talend", "Fivetran"]
    },
    "governance": {
        "ceo": {
            "name": "Dr. Samantha Chen",
            "title": "Chief Executive Officer"
        },
        "boardMembers": [
            {
                "name": "Michael Johnson",
                "title": "Board Chair (Sequoia Capital)"
            }
        ],
        "certifications": ["SOC 2 Type II", "ISO 27001"]
    },
    "digitalPresence": {
        "websiteUrl": "https://nexuswave.example",
        "careersUrl": "https://nexuswave.example/careers",
        "techStack": ["Angular", "Node.js", "Kubernetes", "PostgreSQL"],
        "monthlyVisitors": 125000
    },
    "scrapedData": {
        "sources": [
            "https://nexuswave.example/about",
            "https://crunchbase.com/nexuswave",
            "https://linkedin.com/company/nexuswave"
        ],
        "lastScraped": "2023-11-15T14:30:00Z",
        "confidenceScore": 0.92
    },
    "metaInfo": {
        "lastUpdated": "2023-11-16T09:15:00Z",
        "created": "2020-01-10T10:00:00Z",
        "dataSources": ["scraped", "manual-entry"]
    },
    "customSections": {}
}

# Scraping request model
scrape_model = api.model('ScrapeRequest', {
    'urls': fields.List(fields.String, required=True, description='Website URLs to scrape (1-10 URLs)',
                       example=['https://example.com', 'https://example.com/about']),
    'customInstructions': fields.String(description='Custom instructions for profile generation',
                                      example='Focus on technology stack, recent funding rounds, and key leadership'),
    'documentContent': fields.List(fields.String, description='Extracted text content from uploaded documents',
                                 example=['Company overview document content...', 'Financial report content...']),
    'documentNames': fields.List(fields.String, description='Names of uploaded documents',
                               example=['company_overview.pdf', 'financial_report.docx'])
})

# API Routes
@api.route('/')
class CompanyCreate(Resource):
    @api.doc('create_company')
    @api.expect(company_profile, validate=True, examples={
        'NexusWave Example': {
            'summary': 'Create a complete company profile',
            'description': 'Example of creating a technology company profile with full details',
            'value': example_request
        }
    })
    @api.marshal_with(company_profile, code=201)
    @api.response(400, 'Validation Error')
    @api.response(201, 'Company Created Successfully')
    def post(self):
        """
        Create a new company profile
        """
        try:
            # Generate MongoDB-style ID
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique = str(uuid.uuid4())[:8]
            mongo_id = f"{timestamp}{unique}"

            # Get current timestamp for dates
            current_time = datetime.now()

            # Create default empty objects for all nested fields
            default_company = {
                "id": mongo_id,
                "basicInfo": {
                    "legalName": "",
                    "tradingName": "",
                    "dba": "",
                    "logoUrl": "",
                    "foundedDate": None,
                    "incorporationDate": None,
                    "companyType": "",
                    "industryCodes": []
                },
                "operational": {
                    "headquarters": {
                        "lat": 0.0,
                        "lng": 0.0,
                        "address": ""
                    },
                    "locations": [],
                    "employeeCount": 0,
                    "employeeRange": "",
                    "operatingCountries": [],
                    "subsidiaries": []
                },
                "contact": {
                    "primaryPhone": "",
                    "tollFreePhone": "",
                    "email": "",
                    "investorEmail": "",
                    "socialMedia": []
                },
                "financials": {
                    "stockSymbol": "",
                    "financialData": [],
                    "fundingRounds": []
                },
                "descriptive": {
                    "mission": "",
                    "vision": "",
                    "tagline": "",
                    "description": "",
                    "coreValues": [],
                    "keywords": []
                },
                "relationships": {
                    "keyPeople": [],
                    "productsServices": [],
                    "clients": [],
                    "partners": [],
                    "competitors": []
                },
                "governance": {
                    "ceo": {},
                    "boardMembers": [],
                    "certifications": []
                },
                "digitalPresence": {
                    "websiteUrl": "",
                    "careersUrl": "",
                    "techStack": [],
                    "monthlyVisitors": 0
                },
                "scrapedData": {
                    "sources": [],
                    "lastScraped": None,
                    "confidenceScore": 0.0
                },
                "metaInfo": {
                    "lastUpdated": current_time,
                    "created": current_time,
                    "dataSources": []
                },
                "customSections": {}
            }

            # Update with any provided values from the request
            if api.payload:
                for key, value in api.payload.items():
                    if value is not None and key in default_company:
                        if isinstance(value, dict):
                            default_company[key].update({k: v for k, v in value.items() if v is not None})
                        else:
                            default_company[key] = value

            # Create company instance
            company = Company.from_dict(default_company)
            
            # Add to database
            db.session.add(company)
            db.session.commit()
            
            # Return the created company
            return company_schema.dump(company), 201
        except ValidationException as e:
            api.abort(400, str(e))
        except Exception as e:
            db.session.rollback()
            api.abort(500, str(e))

    def options(self):
        """Handle OPTIONS requests for CORS preflight"""
        return {'Allow': 'GET, POST, PUT, DELETE, OPTIONS'}, 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Fields'
        }

@api.route('/<string:id>')
@api.param('id', 'The company identifier')
class CompanyDetail(Resource):
    @api.doc('get_company')
    @api.marshal_with(company_profile)
    @api.response(404, 'Company not found')
    def get(self, id):
        """Get a specific company profile"""
        try:
            company = Company.query.get(id)
            if not company:
                api.abort(404, f"Company {id} not found")
            return company_schema.dump(company)
        except Exception as e:
            api.abort(500, str(e))

    @api.doc('update_company', body=company_profile)
    @api.expect(company_profile)
    @api.marshal_with(company_profile)
    @api.response(404, 'Company not found')
    @api.response(400, 'Validation Error')
    def put(self, id):
        """Update a company profile"""
        try:
            company = Company.query.get(id)
            if not company:
                api.abort(404, f"Company {id} not found")

            # Update company with provided data
            if api.payload:
                for key, value in api.payload.items():
                    if value is not None and hasattr(company, key):
                        setattr(company, key, value)

            db.session.commit()
            return company_schema.dump(company)
        except ValidationException as e:
            api.abort(400, str(e))
        except Exception as e:
            db.session.rollback()
            api.abort(500, str(e))

    @api.doc('delete_company')
    @api.response(204, 'Company deleted')
    @api.response(404, 'Company not found')
    def delete(self, id):
        """Delete a company profile"""
        try:
            company = Company.query.get(id)
            if not company:
                api.abort(404, f"Company {id} not found")
            
            db.session.delete(company)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            api.abort(500, str(e))

@api.route('/scrape')
class CompanyScrape(Resource):
    @api.doc('scrape_company')
    @api.expect(scrape_model)
    @api.marshal_with(company_profile)
    @api.response(400, 'Invalid URL or scraping failed')
    @api.response(502, 'External service error')
    async def post(self):
        """Scrape company information from multiple URLs and documents"""
        try:
            dto = ScrapeCompanyDTO(**api.payload)
            return await company_service.scrape_company(dto)
        except ValidationException as e:
            api.abort(400, str(e))
        except ExternalServiceException as e:
            api.abort(502, str(e))
        except Exception as e:
            api.abort(500, str(e))

# File upload model for document processing
file_upload_model = api.model('FileUpload', {
    'files': fields.List(fields.Raw, required=True, description='Base64 encoded files with metadata'),
    'maxSizeMB': fields.Integer(default=10, description='Maximum file size in MB')
})

@api.route('/process-files')
class FileProcessor(Resource):
    @api.doc('process_files')
    @api.expect(file_upload_model)
    @api.response(200, 'Files processed successfully')
    @api.response(400, 'Invalid file format or processing failed')
    def post(self):
        """Process uploaded documents and extract text content"""
        try:
            from app.services.file_processing_service import FileProcessingService
            
            file_processor = FileProcessingService()
            payload = api.payload
            
            if not payload.get('files'):
                api.abort(400, 'No files provided')
            
            processed_files = []
            max_size_mb = payload.get('maxSizeMB', 10)
            
            for file_data in payload['files']:
                filename = file_data.get('name', 'unknown')
                content = file_data.get('content', '')
                
                # Validate file size
                if not file_processor.validate_file_size(content, max_size_mb):
                    processed_files.append({
                        'filename': filename,
                        'status': 'error',
                        'message': f'File size exceeds {max_size_mb}MB limit'
                    })
                    continue
                
                # Check if format is supported
                if not file_processor.is_supported_format(filename):
                    processed_files.append({
                        'filename': filename,
                        'status': 'error',
                        'message': f'Unsupported file format. Supported: {file_processor.get_supported_formats()}'
                    })
                    continue
                
                try:
                    # Extract text content
                    text_content = file_processor.extract_text_from_base64(content, filename)
                    processed_files.append({
                        'filename': filename,
                        'status': 'success',
                        'textContent': text_content,
                        'characterCount': len(text_content)
                    })
                except Exception as e:
                    processed_files.append({
                        'filename': filename,
                        'status': 'error',
                        'message': str(e)
                    })
            
            return {
                'processedFiles': processed_files,
                'supportedFormats': file_processor.get_supported_formats(),
                'totalFiles': len(payload['files']),
                'successfulFiles': len([f for f in processed_files if f['status'] == 'success'])
            }
            
        except Exception as e:
            api.abort(500, str(e))

