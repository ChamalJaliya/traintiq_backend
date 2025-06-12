# 🚀 TraintiQ Profile Generator API Documentation

## Overview

The TraintiQ Profile Generator API provides comprehensive company profile generation using advanced AI and multi-source data extraction. This system combines web scraping, natural language processing, and OpenAI's GPT-4 to create detailed, structured company profiles.

**Base URL**: `http://localhost:5000/api`  
**Version**: 2.0.0  
**Authentication**: API Key (X-API-Key header) - Development mode currently

---

## 📚 API Endpoints

### 1. 🚀 Generate Enhanced Company Profile

**POST** `/profile/generate`

Generate a comprehensive company profile using AI-powered analysis of multiple data sources.

#### Request Body
```json
{
    "urls": ["https://www.softcodeit.com", "https://linkedin.com/company/softcodeit"],
    "custom_text": "Focus on AI and machine learning capabilities",
    "focus_areas": ["products", "leadership", "technology"],
    "template": "technology",
    "include_financial": false,
    "include_news": true,
    "max_content_length": 5000,
    "language": "en"
}
```

#### Parameters
- `urls` (required): Array of URLs to analyze
- `custom_text` (optional): Additional context
- `focus_areas` (optional): Specific areas to emphasize
- `template` (optional): Profile template (startup, enterprise, technology, financial)
- `include_financial` (optional): Include financial info
- `include_news` (optional): Include recent news
- `max_content_length` (optional): Max content length per section
- `language` (optional): Content language

#### Response (200 OK)
```json
{
    "success": true,
    "profile_data": {
        "basic_info": {
            "company_name": "SoftCodeIT Solutions",
            "company_overview": "Leading software development company",
            "industry": "Software Development",
            "founded_year": "2018",
            "headquarters": "Colombo, Sri Lanka",
            "company_size": "50-100 employees",
            "website": "https://www.softcodeit.com"
        },
        "products_services": [...],
        "leadership_team": [...],
        "technology_stack": [...],
        "contact_info": {...},
        "company_values": [...],
        "achievements": [...],
        "market_position": "..."
    },
    "metadata": {
        "generation_time": 12.45,
        "sources_processed": 2,
        "ai_model_used": "gpt-4-turbo",
        "content_quality_score": 0.87,
        "tokens_used": 3420
    },
    "message": "Enhanced profile generated successfully"
}
```

---

### 2. 📊 Analyze Data Sources Quality

**GET** `/profile/analyze/sources`

Perform comprehensive analysis of data sources to assess their suitability for profile generation.

#### Query Parameters
- `urls` (required): URLs to analyze (can be repeated)

#### Example Request
```
GET /profile/analyze/sources?urls=https://www.softcodeit.com&urls=https://linkedin.com/company/softcodeit
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
                "sections_found": ["basic_info", "products_services", "contact_info"]
            }
        ]
    },
    "recommendations": [
        "✅ All URLs successfully analyzed",
        "📄 Rich content detected - excellent for comprehensive profile"
    ],
    "message": "Real source analysis completed successfully"
}
```

---

### 3. 📋 Get Available Profile Templates

**GET** `/profile/templates`

Retrieve all available profile templates with their configurations and focus areas.

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

---

### 4. 🏥 System Health Check

**GET** `/profile/health`

Comprehensive health check for all system components and dependencies.

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

---

## 🛠️ Error Handling

### Standard Error Response
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

### Common Error Codes
- **400**: ValidationError - Invalid input parameters
- **401**: AuthenticationError - Invalid or missing API key
- **429**: RateLimitError - Rate limit exceeded
- **500**: InternalServerError - Server processing error
- **503**: ServiceUnavailableError - System temporarily unavailable

---

## 🚀 Quick Start Examples

### cURL Examples

```bash
# 1. Check system health
curl -X GET "http://localhost:5000/api/profile/health"

# 2. Get available templates
curl -X GET "http://localhost:5000/api/profile/templates"

# 3. Analyze data sources
curl -X GET "http://localhost:5000/api/profile/analyze/sources?urls=https://www.softcodeit.com"

# 4. Generate profile
curl -X POST "http://localhost:5000/api/profile/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.softcodeit.com"],
    "template": "technology",
    "focus_areas": ["products", "technology", "leadership"]
  }'
```

### JavaScript/TypeScript Example

```typescript
class ProfileGeneratorService {
  private baseUrl = 'http://localhost:5000/api/profile';

  async generateProfile(request: any) {
    const response = await fetch(`${this.baseUrl}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return await response.json();
  }

  async analyzeSource(urls: string[]) {
    const params = new URLSearchParams();
    urls.forEach(url => params.append('urls', url));
    const response = await fetch(`${this.baseUrl}/analyze/sources?${params}`);
    return await response.json();
  }
}

// Usage
const service = new ProfileGeneratorService();
const result = await service.generateProfile({
  urls: ['https://www.softcodeit.com'],
  template: 'technology'
});
```

### Python Example

```python
import requests

class ProfileGeneratorClient:
    def __init__(self, base_url="http://localhost:5000/api/profile"):
        self.base_url = base_url
    
    def generate_profile(self, urls, template="technology"):
        payload = {"urls": urls, "template": template}
        response = requests.post(f"{self.base_url}/generate", json=payload)
        return response.json()
    
    def analyze_sources(self, urls):
        params = {"urls": urls}
        response = requests.get(f"{self.base_url}/analyze/sources", params=params)
        return response.json()

# Usage
client = ProfileGeneratorClient()
result = client.generate_profile(["https://www.softcodeit.com"])
```

---

## 📊 Performance & Rate Limits

### Rate Limits
- **Profile Generation**: 10 requests/minute
- **Source Analysis**: 20 requests/minute  
- **Template Operations**: 50 requests/minute
- **Health Checks**: 100 requests/minute

### Performance Metrics
- **Average Response Time**: 10-15 seconds for profile generation
- **Success Rate**: 95%+ for valid URLs
- **Content Quality Score**: 0.8-0.95 typical range

---

## 🔧 Development Setup

### Access Swagger Documentation
When the server is running, access interactive API documentation at:
- **Swagger UI**: `http://localhost:5000/api/docs/`
- **ReDoc**: `http://localhost:5000/api/redoc/`

### Environment Variables
- `OPENAI_API_KEY`: Required for AI generation
- `DATABASE_URL`: MySQL connection string
- `REDIS_URL`: Redis connection for caching
- `DEBUG`: Enable debug mode

---

*Last updated: January 2024 | API Version: 2.0.0* 