# 🚀 TraintiQ Profile Generator API Documentation

## Overview

The TraintiQ Profile Generator API provides comprehensive company profile generation using advanced AI and multi-source data extraction. This system combines web scraping, natural language processing, and OpenAI's GPT-4 to create detailed, structured company profiles.

## 🌟 Key Features

- **AI-Powered Generation**: OpenAI GPT-4 for intelligent content synthesis
- **Multi-Source Analysis**: Web scraping, document processing, social media integration
- **Enhanced NLP/NER**: Advanced entity extraction and content categorization
- **Real-time Processing**: Asynchronous generation with progress tracking
- **Template System**: Industry-specific profile templates
- **Quality Assessment**: Source analysis and content validation

## 🔧 Technology Stack

- **Backend**: Flask + FastAPI hybrid architecture
- **AI/ML**: OpenAI GPT-4, LangChain, Sentence Transformers
- **Data Processing**: BeautifulSoup, Selenium, PyPDF2, spaCy
- **Database**: MySQL with SQLAlchemy ORM
- **Async Processing**: Celery with Redis
- **Monitoring**: Prometheus metrics and health checks

## 🚦 Rate Limits & Performance

- **Profile Generation**: 10 requests/minute (avg. 10-15 seconds per request)
- **Source Analysis**: 20 requests/minute (avg. 3-5 seconds per request)
- **Template Operations**: 50 requests/minute (instant response)
- **Success Rate**: 95%+ for valid URLs
- **Content Quality**: Typically 0.8-0.95 quality score

## 🔐 Authentication

Currently in development mode. Production deployment will require API keys via `X-API-Key` header.

## 📈 Response Format

All responses follow a consistent structure:

```json
{
    "success": true/false,
    "data": { ... },
    "message": "Human-readable message",
    "metadata": { "generation_time": 12.5, ... }
}
```

---

# 📚 API Endpoints

## 🚀 Profile Generation

### Generate Enhanced Company Profile

**Endpoint**: `POST /api/profile/generate`

Generate a comprehensive company profile using AI-powered analysis of multiple data sources.

#### Request Body

```json
{
    "urls": [
        "https://www.softcodeit.com",
        "https://linkedin.com/company/softcodeit"
    ],
    "custom_text": "Focus on the company's AI and machine learning capabilities",
    "focus_areas": ["products", "leadership", "technology", "achievements"],
    "template": "technology",
    "include_financial": false,
    "include_news": true,
    "max_content_length": 5000,
    "language": "en"
}
```

#### Request Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `urls` | Array[String] | ✅ | URLs to analyze for profile generation | `["https://www.company.com"]` |
| `custom_text` | String | ❌ | Additional context or instructions | `"Focus on AI capabilities"` |
| `focus_areas` | Array[String] | ❌ | Specific areas to emphasize | `["products", "leadership"]` |
| `template` | String | ❌ | Profile template to use | `"technology"` |
| `include_financial` | Boolean | ❌ | Include financial information | `false` |
| `include_news` | Boolean | ❌ | Include recent news and updates | `true` |
| `max_content_length` | Integer | ❌ | Maximum content length per section | `5000` |
| `language` | String | ❌ | Content language | `"en"` |

#### Template Options

| Template | Description | Focus Areas |
|----------|-------------|-------------|
| `startup` | Early-stage companies and startups | Innovation, funding, growth potential |
| `enterprise` | Established large corporations | History, financials, comprehensive coverage |
| `technology` | Tech companies and software businesses | Technology stack, products, innovation |
| `financial` | Banks, fintech, financial institutions | Financial services, compliance, regulatory |

#### Response

```json
{
    "success": true,
    "profile_data": {
        "basic_info": {
            "company_name": "SoftCodeIT Solutions",
            "company_overview": "Leading software development company specializing in custom web and mobile applications",
            "industry": "Software Development",
            "founded_year": "2018",
            "headquarters": "Colombo, Sri Lanka",
            "company_size": "50-100 employees",
            "website": "https://www.softcodeit.com"
        },
        "products_services": [
            {
                "name": "Custom Web Development",
                "description": "End-to-end web application development using modern frameworks",
                "category": "Web Development",
                "features": ["React/Angular frontend", "Node.js/Python backend", "Cloud deployment"]
            }
        ],
        "leadership_team": [
            {
                "name": "John Smith",
                "position": "Chief Technology Officer",
                "bio": "15+ years experience in software architecture and team leadership",
                "experience": "15+ years in software development",
                "linkedin": "https://linkedin.com/in/johnsmith"
            }
        ],
        "technology_stack": [
            {
                "name": "React",
                "category": "Frontend Framework",
                "description": "Primary frontend framework for web applications",
                "version": "18.x"
            }
        ],
        "contact_info": {
            "email": "info@softcodeit.com",
            "phone": "+94 11 234 5678",
            "address": "123 Tech Street, Colombo 03, Sri Lanka",
            "social_media": {
                "linkedin": "https://linkedin.com/company/softcodeit",
                "twitter": "@softcodeit"
            }
        },
        "company_values": ["Innovation", "Quality", "Customer Focus", "Integrity"],
        "achievements": ["ISO 9001 Certified", "Top Software Company 2023", "500+ Projects Delivered"],
        "market_position": "Leading provider of custom software solutions in South Asia"
    },
    "metadata": {
        "generation_time": 12.45,
        "sources_processed": 2,
        "ai_model_used": "gpt-4-turbo",
        "content_quality_score": 0.87,
        "data_sources": ["https://www.softcodeit.com", "https://linkedin.com/company/softcodeit"],
        "processing_method": "enhanced_ai_generation",
        "tokens_used": 3420,
        "generation_timestamp": "2024-01-15T10:30:00Z"
    },
    "message": "Enhanced profile generated successfully"
}
```

#### Process Overview

1. **Source Validation**: Validate and analyze provided URLs
2. **Data Extraction**: Scrape content using advanced techniques (requests + Selenium fallback)
3. **AI Processing**: Use OpenAI GPT-4 for intelligent content synthesis
4. **Structured Output**: Organize data into categorized sections
5. **Quality Assessment**: Validate and score generated content

#### Supported Data Sources

- Company websites and landing pages
- LinkedIn company profiles
- Crunchbase and similar business directories
- Social media profiles
- News articles and press releases

---

## 📊 Data Source Analysis

### Analyze Data Sources Quality

**Endpoint**: `GET /api/profile/analyze/sources`

Perform comprehensive analysis of data sources to assess their suitability for profile generation.

#### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `urls` | Array[String] | ✅ | URLs to analyze (can be repeated) | `?urls=https://company.com&urls=https://linkedin.com/company/example` |

#### Example Request

```
GET /api/profile/analyze/sources?urls=https://www.softcodeit.com&urls=https://linkedin.com/company/softcodeit
```

#### Response

```json
{
    "success": true,
    "analysis": {
        "total_sources": 2,
        "valid_sources": 2,
        "successful_scrapes": 2,
        "failed_scrapes": 0,
        "total_content_length": 45680,
        "average_content_length": 22840.0,
        "source_quality": "excellent",
        "domains_analyzed": ["softcodeit.com", "linkedin.com"],
        "detailed_results": [
            {
                "url": "https://www.softcodeit.com",
                "status": "success",
                "content_length": 15420,
                "response_time": 2.34,
                "scraping_method": "requests",
                "has_company_info": true,
                "sections_found": ["basic_info", "products_services", "contact_info"]
            },
            {
                "url": "https://linkedin.com/company/softcodeit",
                "status": "success",
                "content_length": 30260,
                "response_time": 3.12,
                "scraping_method": "requests",
                "has_company_info": true,
                "sections_found": ["basic_info", "leadership_team", "company_updates"]
            }
        ],
        "analysis_timestamp": "2024-01-15T10:25:00Z"
    },
    "recommendations": [
        "✅ All URLs successfully analyzed",
        "📄 Rich content detected - excellent for comprehensive profile",
        "🚀 High-quality sources - expect excellent profile generation results"
    ],
    "message": "Real source analysis completed successfully"
}
```

#### Analysis Capabilities

- **Content Quality**: Assess content richness and relevance
- **Accessibility**: Test URL accessibility and response times
- **Data Extraction**: Validate successful content extraction
- **Company Information**: Detect presence of company-specific data
- **Performance Metrics**: Measure response times and content volume

#### Quality Assessment Criteria

- **Excellent**: All URLs accessible, rich content, comprehensive company info
- **Good**: Most URLs accessible, adequate content for profile generation
- **Poor**: Limited accessibility or insufficient content

---

## 📋 Template Management

### Get Available Profile Templates

**Endpoint**: `GET /api/profile/templates`

Retrieve all available profile templates with their configurations and focus areas.

#### Response

```json
{
    "success": true,
    "templates": {
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
    },
    "message": "Templates retrieved successfully"
}
```

#### Template Details

##### 🚀 Startup Template
- **Purpose**: Early-stage companies and startups
- **Focus**: Innovation, growth potential, funding, market opportunity
- **Sections**: Overview, products, leadership, market analysis, funding status

##### 🏢 Enterprise Template
- **Purpose**: Established large corporations
- **Focus**: Comprehensive coverage, history, financial performance
- **Sections**: Overview, history, products, leadership, financials, market position

##### 💻 Technology Template
- **Purpose**: Tech companies and software businesses
- **Focus**: Technology stack, innovation, products, technical leadership
- **Sections**: Overview, products, technology, leadership, innovation, market

##### 💰 Financial Template
- **Purpose**: Banks, fintech, financial institutions
- **Focus**: Financial services, compliance, regulatory information
- **Sections**: Overview, history, products, leadership, financials, compliance

---

## 🏥 System Health Monitoring

### System Health Check

**Endpoint**: `GET /api/profile/health`

Comprehensive health check for all system components and dependencies.

#### Response

```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "2.0.0",
    "services": {
        "database": "healthy",
        "openai_api": "healthy",
        "scraping_service": "healthy",
        "redis_cache": "healthy"
    },
    "uptime": 86400.5,
    "memory_usage": {
        "total": "8GB",
        "used": "2.1GB",
        "available": "5.9GB",
        "percentage": 26.25
    },
    "database_status": "connected"
}
```

#### Monitored Components

- **Database**: MySQL connection and query performance
- **OpenAI API**: API connectivity and rate limit status
- **Scraping Service**: Web scraping capability and browser availability
- **Redis Cache**: Cache connectivity and performance
- **Memory Usage**: System memory consumption
- **Service Uptime**: Application uptime tracking

#### Health Status Levels

- **healthy**: All systems operational
- **degraded**: Some non-critical issues detected
- **unhealthy**: Critical systems failing

---

# 🛠️ Error Handling

## Error Response Format

All errors follow a consistent format:

```json
{
    "success": false,
    "error": "ValidationError",
    "message": "Invalid URL format provided",
    "details": {
        "invalid_urls": ["invalid-url"],
        "valid_formats": ["http://", "https://"]
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Common Error Codes

| HTTP Code | Error Type | Description | Solution |
|-----------|------------|-------------|----------|
| 400 | ValidationError | Invalid input parameters | Check request format and required fields |
| 401 | AuthenticationError | Invalid or missing API key | Provide valid X-API-Key header |
| 429 | RateLimitError | Rate limit exceeded | Wait before making more requests |
| 500 | InternalServerError | Server processing error | Check system health, retry request |
| 503 | ServiceUnavailableError | System temporarily unavailable | Check health endpoint, retry later |

---

# 🚀 Getting Started

## Quick Start Example

```bash
# 1. Analyze data sources
curl -X GET "http://localhost:5000/api/profile/analyze/sources?urls=https://www.softcodeit.com"

# 2. Generate profile
curl -X POST "http://localhost:5000/api/profile/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.softcodeit.com"],
    "template": "technology",
    "focus_areas": ["products", "technology", "leadership"]
  }'

# 3. Check system health
curl -X GET "http://localhost:5000/api/profile/health"
```

## Integration Examples

### JavaScript/TypeScript

```typescript
// Profile generation service
class ProfileGeneratorService {
  private baseUrl = 'http://localhost:5000/api/profile';

  async generateProfile(request: ProfileGenerationRequest): Promise<ProfileResponse> {
    const response = await fetch(`${this.baseUrl}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      throw new Error(`Profile generation failed: ${response.statusText}`);
    }
    
    return await response.json();
  }

  async analyzeSource(urls: string[]): Promise<SourceAnalysisResponse> {
    const params = new URLSearchParams();
    urls.forEach(url => params.append('urls', url));
    
    const response = await fetch(`${this.baseUrl}/analyze/sources?${params}`);
    return await response.json();
  }
}
```

### Python

```python
import requests
from typing import List, Dict, Any

class ProfileGeneratorClient:
    def __init__(self, base_url: str = "http://localhost:5000/api/profile"):
        self.base_url = base_url
    
    def generate_profile(self, urls: List[str], template: str = "technology", 
                        focus_areas: List[str] = None) -> Dict[str, Any]:
        """Generate company profile from URLs"""
        payload = {
            "urls": urls,
            "template": template,
            "focus_areas": focus_areas or ["products", "leadership", "technology"]
        }
        
        response = requests.post(f"{self.base_url}/generate", json=payload)
        response.raise_for_status()
        return response.json()
    
    def analyze_sources(self, urls: List[str]) -> Dict[str, Any]:
        """Analyze data source quality"""
        params = {"urls": urls}
        response = requests.get(f"{self.base_url}/analyze/sources", params=params)
        response.raise_for_status()
        return response.json()

# Usage example
client = ProfileGeneratorClient()
result = client.generate_profile(
    urls=["https://www.softcodeit.com"],
    template="technology"
)
print(f"Generated profile for: {result['profile_data']['basic_info']['company_name']}")
```

---

# 📊 Performance & Monitoring

## Performance Metrics

- **Average Response Time**: 10-15 seconds for profile generation
- **Success Rate**: 95%+ for valid URLs
- **Content Quality Score**: 0.8-0.95 typical range
- **Concurrent Requests**: Up to 10 simultaneous profile generations
- **Cache Hit Rate**: 85%+ for repeated requests

## Monitoring Endpoints

- **Health Check**: `/api/profile/health` - System status
- **Metrics**: `/metrics` - Prometheus metrics (if enabled)
- **Logs**: Application logs available via Docker/system logs

## Best Practices

1. **Source Selection**: Use official company websites and verified business profiles
2. **Template Matching**: Choose templates that match the company type and industry
3. **Focus Areas**: Specify relevant focus areas for better content quality
4. **Error Handling**: Implement proper error handling and retry logic
5. **Rate Limiting**: Respect rate limits to ensure system stability

---

# 🔧 Development & Deployment

## Local Development

```bash
# Start the backend server
cd traintiq_scrapping_backend
python run.py

# Access Swagger documentation
open http://localhost:5000/api/docs/

# Test API endpoints
curl http://localhost:5000/api/profile/health
```

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access API documentation
open http://localhost:5000/api/docs/
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI generation | Required |
| `DATABASE_URL` | MySQL database connection string | `mysql://...` |
| `REDIS_URL` | Redis connection for caching | `redis://localhost:6379` |
| `DEBUG` | Enable debug mode | `False` |
| `MAX_WORKERS` | Maximum concurrent workers | `4` |

---

# 📞 Support & Contact

- **Documentation**: Available at `/api/docs/` when server is running
- **Issues**: Report issues via GitHub or contact development team
- **Email**: dev@traintiq.com
- **License**: MIT License

---

*Last updated: January 2024*
*API Version: 2.0.0* 