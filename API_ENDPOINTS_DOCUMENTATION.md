# 🚀 TraintiQ Profile Generator API Endpoints Documentation

## Overview

This document provides comprehensive documentation for all TraintiQ Profile Generator API endpoints. The system provides AI-powered company profile generation using multi-source data extraction and advanced natural language processing.

## 🌐 Base URL

- **Development**: `http://localhost:5000/api`
- **Production**: `https://api.traintiq.com/api`

## 🔐 Authentication

Currently in development mode. Production will require API keys via `X-API-Key` header.

## 📊 Response Format

All API responses follow this consistent structure:

```json
{
    "success": true/false,
    "data": { ... },
    "message": "Human-readable message",
    "metadata": { ... },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

---

# 📚 API Endpoints

## 1. 🚀 Profile Generation

### POST /profile/generate

Generate a comprehensive company profile using AI-powered analysis of multiple data sources.

#### Request

**Headers:**
```
Content-Type: application/json
X-API-Key: your-api-key (production only)
```

**Body:**
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

| Parameter | Type | Required | Description | Default | Example |
|-----------|------|----------|-------------|---------|---------|
| `urls` | Array[String] | ✅ | URLs to analyze for profile generation | - | `["https://www.company.com"]` |
| `custom_text` | String | ❌ | Additional context or instructions | null | `"Focus on AI capabilities"` |
| `focus_areas` | Array[String] | ❌ | Specific areas to emphasize | `["overview", "products"]` | `["products", "leadership"]` |
| `template` | String | ❌ | Profile template to use | `"enterprise"` | `"technology"` |
| `include_financial` | Boolean | ❌ | Include financial information | `false` | `true` |
| `include_news` | Boolean | ❌ | Include recent news and updates | `true` | `false` |
| `max_content_length` | Integer | ❌ | Maximum content length per section | `5000` | `3000` |
| `language` | String | ❌ | Content language | `"en"` | `"es"` |

#### Template Options

| Template | Description | Focus Areas |
|----------|-------------|-------------|
| `startup` | Early-stage companies and startups | Innovation, funding, growth potential |
| `enterprise` | Established large corporations | History, financials, comprehensive coverage |
| `technology` | Tech companies and software businesses | Technology stack, products, innovation |
| `financial` | Banks, fintech, financial institutions | Financial services, compliance, regulatory |

#### Response (200 OK)

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
            },
            {
                "name": "Mobile App Development",
                "description": "Native and cross-platform mobile applications",
                "category": "Mobile Development",
                "features": ["iOS/Android", "React Native", "Flutter"]
            }
        ],
        "leadership_team": [
            {
                "name": "John Smith",
                "position": "Chief Technology Officer",
                "bio": "15+ years experience in software architecture and team leadership",
                "experience": "15+ years in software development",
                "linkedin": "https://linkedin.com/in/johnsmith"
            },
            {
                "name": "Jane Doe",
                "position": "Chief Executive Officer",
                "bio": "Visionary leader with expertise in business strategy and growth",
                "experience": "12+ years in business leadership"
            }
        ],
        "technology_stack": [
            {
                "name": "React",
                "category": "Frontend Framework",
                "description": "Primary frontend framework for web applications",
                "version": "18.x"
            },
            {
                "name": "Node.js",
                "category": "Backend Runtime",
                "description": "Server-side JavaScript runtime",
                "version": "20.x"
            },
            {
                "name": "MongoDB",
                "category": "Database",
                "description": "NoSQL database for flexible data storage",
                "version": "7.x"
            }
        ],
        "contact_info": {
            "email": "info@softcodeit.com",
            "phone": "+94 11 234 5678",
            "address": "123 Tech Street, Colombo 03, Sri Lanka",
            "social_media": {
                "linkedin": "https://linkedin.com/company/softcodeit",
                "twitter": "@softcodeit",
                "facebook": "https://facebook.com/softcodeit"
            }
        },
        "company_values": ["Innovation", "Quality", "Customer Focus", "Integrity"],
        "achievements": [
            "ISO 9001 Certified",
            "Top Software Company 2023",
            "500+ Projects Delivered",
            "99.9% Client Satisfaction Rate"
        ],
        "market_position": "Leading provider of custom software solutions in South Asia",
        "recent_news": [
            "Launched new AI-powered development platform",
            "Expanded operations to Singapore market",
            "Received Best Innovation Award 2024"
        ]
    },
    "metadata": {
        "generation_time": 12.45,
        "sources_processed": 2,
        "ai_model_used": "gpt-4-turbo",
        "content_quality_score": 0.87,
        "data_sources": [
            "https://www.softcodeit.com",
            "https://linkedin.com/company/softcodeit"
        ],
        "processing_method": "enhanced_ai_generation",
        "tokens_used": 3420,
        "generation_timestamp": "2024-01-15T10:30:00Z"
    },
    "message": "Enhanced profile generated successfully"
}
```

#### Error Responses

**400 Bad Request:**
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

**500 Internal Server Error:**
```json
{
    "success": false,
    "error": "InternalServerError",
    "message": "Profile generation failed due to AI service error",
    "details": {
        "error_code": "AI_SERVICE_UNAVAILABLE",
        "retry_after": 30
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

#### cURL Example

```bash
curl -X POST "http://localhost:5000/api/profile/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.softcodeit.com"],
    "template": "technology",
    "focus_areas": ["products", "technology", "leadership"],
    "custom_text": "Focus on AI and machine learning capabilities"
  }'
```

---

## 2. 📊 Source Analysis

### GET /profile/analyze/sources

Perform comprehensive analysis of data sources to assess their suitability for profile generation.

#### Request

**Query Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `urls` | Array[String] | ✅ | URLs to analyze (can be repeated) | `?urls=https://company.com&urls=https://linkedin.com/company/example` |

#### Example Request

```
GET /api/profile/analyze/sources?urls=https://www.softcodeit.com&urls=https://linkedin.com/company/softcodeit
```

#### Response (200 OK)

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
                "sections_found": ["basic_info", "products_services", "contact_info", "leadership_team"]
            },
            {
                "url": "https://linkedin.com/company/softcodeit",
                "status": "success",
                "content_length": 30260,
                "response_time": 3.12,
                "scraping_method": "requests",
                "has_company_info": true,
                "sections_found": ["basic_info", "leadership_team", "company_updates", "employee_info"]
            }
        ],
        "analysis_timestamp": "2024-01-15T10:25:00Z"
    },
    "recommendations": [
        "✅ All URLs successfully analyzed",
        "📄 Rich content detected - excellent for comprehensive profile",
        "🚀 High-quality sources - expect excellent profile generation results",
        "💡 Consider adding social media profiles for enhanced leadership information"
    ],
    "message": "Real source analysis completed successfully"
}
```

#### Quality Assessment Criteria

- **Excellent**: All URLs accessible, rich content, comprehensive company info
- **Good**: Most URLs accessible, adequate content for profile generation
- **Poor**: Limited accessibility or insufficient content

#### cURL Example

```bash
curl -X GET "http://localhost:5000/api/profile/analyze/sources?urls=https://www.softcodeit.com&urls=https://linkedin.com/company/softcodeit"
```

---

## 3. 📋 Template Management

### GET /profile/templates

Retrieve all available profile templates with their configurations and focus areas.

#### Request

No parameters required.

#### Response (200 OK)

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
- **Best For**: Companies < 5 years old, seeking investment, rapid growth phase

##### 🏢 Enterprise Template
- **Purpose**: Established large corporations
- **Focus**: Comprehensive coverage, history, financial performance
- **Sections**: Overview, history, products, leadership, financials, market position
- **Best For**: Large corporations, public companies, established market leaders

##### 💻 Technology Template
- **Purpose**: Tech companies and software businesses
- **Focus**: Technology stack, innovation, products, technical leadership
- **Sections**: Overview, products, technology, leadership, innovation, market
- **Best For**: Software companies, SaaS providers, tech startups, IT services

##### 💰 Financial Template
- **Purpose**: Banks, fintech, financial institutions
- **Focus**: Financial services, compliance, regulatory information
- **Sections**: Overview, history, products, leadership, financials, compliance
- **Best For**: Banks, insurance companies, fintech startups, investment firms

#### cURL Example

```bash
curl -X GET "http://localhost:5000/api/profile/templates"
```

---

## 4. 🏥 System Health Monitoring

### GET /profile/health

Comprehensive health check for all system components and dependencies.

#### Request

No parameters required.

#### Response (200 OK)

```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "2.0.0",
    "services": {
        "database": "healthy",
        "openai_api": "healthy",
        "scraping_service": "healthy",
        "redis_cache": "healthy",
        "celery_workers": "healthy"
    },
    "uptime": 86400.5,
    "memory_usage": {
        "total": "8GB",
        "used": "2.1GB",
        "available": "5.9GB",
        "percentage": 26.25
    },
    "database_status": "connected",
    "performance_metrics": {
        "avg_response_time": 2.34,
        "requests_per_minute": 45,
        "success_rate": 0.97,
        "cache_hit_rate": 0.85
    }
}
```

#### Health Status Levels

- **healthy**: All systems operational
- **degraded**: Some non-critical issues detected
- **unhealthy**: Critical systems failing

#### Monitored Components

- **Database**: MySQL connection and query performance
- **OpenAI API**: API connectivity and rate limit status
- **Scraping Service**: Web scraping capability and browser availability
- **Redis Cache**: Cache connectivity and performance
- **Celery Workers**: Background task processing status
- **Memory Usage**: System memory consumption
- **Service Uptime**: Application uptime tracking

#### Response (503 Service Unavailable)

```json
{
    "status": "unhealthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "2.0.0",
    "services": {
        "database": "unhealthy",
        "openai_api": "healthy",
        "scraping_service": "degraded",
        "redis_cache": "healthy"
    },
    "errors": [
        "Database connection timeout",
        "Scraping service response time > 10s"
    ],
    "message": "System experiencing issues - some services unavailable"
}
```

#### cURL Example

```bash
curl -X GET "http://localhost:5000/api/profile/health"
```

---

# 🛠️ Error Handling

## Standard Error Response Format

All API errors follow this consistent format:

```json
{
    "success": false,
    "error": "ErrorType",
    "message": "Human-readable error description",
    "details": {
        "additional": "context",
        "error_code": "SPECIFIC_ERROR_CODE"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Common Error Codes

| HTTP Code | Error Type | Description | Common Causes | Solution |
|-----------|------------|-------------|---------------|----------|
| 400 | ValidationError | Invalid input parameters | Missing required fields, invalid URL format | Check request format and required fields |
| 401 | AuthenticationError | Invalid or missing API key | Missing X-API-Key header | Provide valid X-API-Key header |
| 403 | AuthorizationError | Insufficient permissions | Invalid API key permissions | Check API key permissions |
| 429 | RateLimitError | Rate limit exceeded | Too many requests | Wait before making more requests |
| 500 | InternalServerError | Server processing error | AI service error, database issues | Check system health, retry request |
| 502 | BadGatewayError | External service error | OpenAI API unavailable | Check external service status |
| 503 | ServiceUnavailableError | System temporarily unavailable | Maintenance, overload | Check health endpoint, retry later |
| 504 | TimeoutError | Request timeout | Long-running operation | Increase timeout, retry request |

## Error Examples

### Validation Error (400)
```json
{
    "success": false,
    "error": "ValidationError",
    "message": "Invalid URL format provided",
    "details": {
        "invalid_urls": ["not-a-url", "ftp://invalid.com"],
        "valid_formats": ["http://", "https://"],
        "field": "urls"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Rate Limit Error (429)
```json
{
    "success": false,
    "error": "RateLimitError",
    "message": "Rate limit exceeded for profile generation",
    "details": {
        "limit": 10,
        "window": "1 minute",
        "retry_after": 45,
        "current_usage": 10
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Internal Server Error (500)
```json
{
    "success": false,
    "error": "InternalServerError",
    "message": "AI service temporarily unavailable",
    "details": {
        "error_code": "AI_SERVICE_TIMEOUT",
        "service": "openai_api",
        "retry_after": 30
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

---

# 🚀 Integration Examples

## JavaScript/TypeScript

```typescript
interface ProfileGenerationRequest {
  urls: string[];
  template?: 'startup' | 'enterprise' | 'technology' | 'financial';
  focus_areas?: string[];
  custom_text?: string;
  include_financial?: boolean;
  include_news?: boolean;
  max_content_length?: number;
  language?: string;
}

interface ProfileGenerationResponse {
  success: boolean;
  profile_data: {
    basic_info: CompanyBasicInfo;
    products_services?: ProductService[];
    leadership_team?: LeadershipMember[];
    technology_stack?: TechnologyItem[];
    contact_info?: ContactInfo;
    company_values?: string[];
    achievements?: string[];
    market_position?: string;
    recent_news?: string[];
  };
  metadata: GenerationMetadata;
  message: string;
}

class ProfileGeneratorService {
  private baseUrl = 'http://localhost:5000/api/profile';
  private apiKey?: string;

  constructor(apiKey?: string) {
    this.apiKey = apiKey;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }
    
    return headers;
  }

  async generateProfile(request: ProfileGenerationRequest): Promise<ProfileGenerationResponse> {
    const response = await fetch(`${this.baseUrl}/generate`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Profile generation failed: ${error.message}`);
    }
    
    return await response.json();
  }

  async analyzeSource(urls: string[]): Promise<SourceAnalysisResponse> {
    const params = new URLSearchParams();
    urls.forEach(url => params.append('urls', url));
    
    const response = await fetch(`${this.baseUrl}/analyze/sources?${params}`, {
      headers: this.getHeaders()
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Source analysis failed: ${error.message}`);
    }
    
    return await response.json();
  }

  async getTemplates(): Promise<TemplatesResponse> {
    const response = await fetch(`${this.baseUrl}/templates`, {
      headers: this.getHeaders()
    });
    
    return await response.json();
  }

  async checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    return await response.json();
  }
}

// Usage example
const service = new ProfileGeneratorService('your-api-key');

try {
  const result = await service.generateProfile({
    urls: ['https://www.softcodeit.com'],
    template: 'technology',
    focus_areas: ['products', 'technology', 'leadership']
  });
  
  console.log('Generated profile:', result.profile_data.basic_info.company_name);
} catch (error) {
  console.error('Profile generation failed:', error.message);
}
```

## Python

```python
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

@dataclass
class ProfileGenerationRequest:
    urls: List[str]
    template: Optional[str] = None
    focus_areas: Optional[List[str]] = None
    custom_text: Optional[str] = None
    include_financial: bool = False
    include_news: bool = True
    max_content_length: int = 5000
    language: str = "en"

class ProfileGeneratorClient:
    def __init__(self, base_url: str = "http://localhost:5000/api/profile", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
    
    def generate_profile(self, request: ProfileGenerationRequest) -> Dict[str, Any]:
        """Generate company profile from URLs"""
        payload = {
            "urls": request.urls,
            "template": request.template,
            "focus_areas": request.focus_areas,
            "custom_text": request.custom_text,
            "include_financial": request.include_financial,
            "include_news": request.include_news,
            "max_content_length": request.max_content_length,
            "language": request.language
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        response = self.session.post(f"{self.base_url}/generate", json=payload)
        response.raise_for_status()
        return response.json()
    
    def analyze_sources(self, urls: List[str]) -> Dict[str, Any]:
        """Analyze data source quality"""
        params = {"urls": urls}
        response = self.session.get(f"{self.base_url}/analyze/sources", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_templates(self) -> Dict[str, Any]:
        """Get available profile templates"""
        response = self.session.get(f"{self.base_url}/templates")
        response.raise_for_status()
        return response.json()
    
    def check_health(self) -> Dict[str, Any]:
        """Check system health"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()  # Don't raise for status to handle unhealthy responses

# Usage example
client = ProfileGeneratorClient(api_key="your-api-key")

try:
    # Analyze sources first
    analysis = client.analyze_sources(["https://www.softcodeit.com"])
    print(f"Source quality: {analysis['analysis']['source_quality']}")
    
    # Generate profile
    request = ProfileGenerationRequest(
        urls=["https://www.softcodeit.com"],
        template="technology",
        focus_areas=["products", "technology", "leadership"]
    )
    
    result = client.generate_profile(request)
    print(f"Generated profile for: {result['profile_data']['basic_info']['company_name']}")
    print(f"Generation time: {result['metadata']['generation_time']} seconds")
    
except requests.exceptions.HTTPError as e:
    print(f"API error: {e.response.json()['message']}")
except Exception as e:
    print(f"Error: {str(e)}")
```

## cURL Examples

### Complete Workflow

```bash
#!/bin/bash

# Set base URL and API key
BASE_URL="http://localhost:5000/api/profile"
API_KEY="your-api-key"  # Optional for development

# 1. Check system health
echo "Checking system health..."
curl -s -X GET "$BASE_URL/health" | jq '.'

# 2. Get available templates
echo -e "\nGetting available templates..."
curl -s -X GET "$BASE_URL/templates" | jq '.templates'

# 3. Analyze data sources
echo -e "\nAnalyzing data sources..."
curl -s -X GET "$BASE_URL/analyze/sources?urls=https://www.softcodeit.com" | jq '.analysis.source_quality'

# 4. Generate profile
echo -e "\nGenerating profile..."
curl -s -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "urls": ["https://www.softcodeit.com"],
    "template": "technology",
    "focus_areas": ["products", "technology", "leadership"],
    "custom_text": "Focus on AI and machine learning capabilities"
  }' | jq '.profile_data.basic_info.company_name'
```

---

# 📊 Performance & Best Practices

## Performance Metrics

- **Average Response Time**: 10-15 seconds for profile generation
- **Success Rate**: 95%+ for valid URLs
- **Content Quality Score**: 0.8-0.95 typical range
- **Concurrent Requests**: Up to 10 simultaneous profile generations
- **Cache Hit Rate**: 85%+ for repeated requests

## Rate Limits

| Endpoint | Limit | Window | Burst |
|----------|-------|--------|-------|
| `/profile/generate` | 10 requests | 1 minute | 2 requests |
| `/profile/analyze/sources` | 20 requests | 1 minute | 5 requests |
| `/profile/templates` | 50 requests | 1 minute | 10 requests |
| `/profile/health` | 100 requests | 1 minute | 20 requests |

## Best Practices

### 1. Source Selection
- Use official company websites as primary sources
- Include LinkedIn company profiles for leadership information
- Add Crunchbase or similar business directories for comprehensive data
- Avoid personal blogs or unofficial sources

### 2. Template Selection
- **Startup**: Companies < 5 years old, seeking funding
- **Enterprise**: Large corporations, public companies
- **Technology**: Software companies, SaaS providers, IT services
- **Financial**: Banks, fintech, investment firms

### 3. Focus Areas Optimization
- Specify 3-5 focus areas for best results
- Match focus areas to your use case
- Common combinations:
  - Sales: `["overview", "products", "market", "achievements"]`
  - Investment: `["overview", "leadership", "financials", "market"]`
  - Partnership: `["overview", "products", "technology", "contact_info"]`

### 4. Error Handling
```typescript
async function generateProfileWithRetry(request: ProfileGenerationRequest, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await service.generateProfile(request);
    } catch (error) {
      if (error.status === 429) {
        // Rate limit - wait and retry
        const retryAfter = error.details?.retry_after || 60;
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
        continue;
      }
      
      if (error.status >= 500 && attempt < maxRetries) {
        // Server error - retry with exponential backoff
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
        continue;
      }
      
      throw error;
    }
  }
}
```

### 5. Caching Strategy
- Cache template responses (rarely change)
- Cache source analysis for 1 hour
- Cache generated profiles for 24 hours
- Use ETags for conditional requests

---

# 🔧 Development & Testing

## Local Development Setup

```bash
# Start the backend server
cd traintiq_scrapping_backend
python run.py

# Access API documentation
open http://localhost:5000/api/docs/

# Test endpoints
curl http://localhost:5000/api/profile/health
```

## Testing Endpoints

### Unit Tests
```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get('/api/profile/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] in ['healthy', 'degraded', 'unhealthy']

def test_templates_endpoint(client):
    response = client.get('/api/profile/templates')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'templates' in data
```

### Integration Tests
```bash
# Test complete workflow
./test_api_workflow.sh

# Load testing
ab -n 100 -c 10 http://localhost:5000/api/profile/health

# Performance testing
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:5000/api/profile/generate
```

---

# 📞 Support & Resources

## Documentation Links
- **Interactive API Docs**: `http://localhost:5000/api/docs/` (when server is running)
- **OpenAPI Specification**: Available in `swagger.yaml`
- **Postman Collection**: Import from `/docs/postman_collection.json`

## Support Channels
- **Email**: dev@traintiq.com
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive guides and examples

## Changelog
- **v2.0.0**: Enhanced AI generation, improved templates, comprehensive documentation
- **v1.5.0**: Added source analysis, health monitoring
- **v1.0.0**: Initial release with basic profile generation

---

*Last updated: January 2024*
*API Version: 2.0.0* 