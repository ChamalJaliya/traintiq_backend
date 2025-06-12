# TraintiQ Backend API

A powerful Python Flask backend for AI-powered company profile generation with advanced web scraping, natural language processing, and machine learning capabilities.

## Features

- 🤖 **AI-Powered Profile Generation**: Advanced GPT-4 integration for intelligent content generation
- 🌐 **Web Scraping**: Robust scraping engine with content extraction and processing
- 📊 **NLP Processing**: spaCy integration for entity extraction and text analysis
- 🔍 **Semantic Search**: Vector embeddings for intelligent content matching
- 💬 **Chat API**: Interactive chat interface with conversation memory
- 📈 **Async Processing**: Celery integration for background task processing
- 🛡️ **Error Handling**: Comprehensive error handling with fallback mechanisms

## Architecture

### Service Organization

```
app/services/
├── ai/                 # AI & Machine Learning Services
│   ├── chat_service.py           # Chat functionality with OpenAI
│   ├── prompt_engine.py          # Prompt templates and management
│   ├── knowledge_base.py         # Vector embeddings and search
│   └── profile_generator.py      # AI profile generation
├── data/               # Data Processing Services
│   ├── scraping_service.py       # Web scraping and content extraction
│   ├── data_extraction_service.py # Data parsing and extraction
│   ├── document_processor.py     # Document processing and analysis
│   └── file_processing_service.py # File handling and processing
└── core/               # Core Business Services
    ├── base_service.py           # Base service class
    ├── company_service.py        # Company data management
    ├── celery_tasks.py          # Background task processing
    └── profile_generation_service.py # Profile generation orchestration
```

## Prerequisites

- Python 3.10+
- pip and virtualenv
- OpenAI API key
- MySQL database (optional)
- Redis (for Celery, optional)

## Manual Development Setup

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download Required Models
```bash
# Download spaCy English model
python -m spacy download en_core_web_sm
```

### 3. Environment Configuration
Create `config.env` file:
```env
# API Configuration
FLASK_ENV=development
FLASK_DEBUG=True
API_PORT=5000

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Database Configuration (Optional)
DATABASE_URL=mysql://user:password@localhost/traintiq
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=traintiq

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 4. Database Setup (Optional)
```bash
# Initialize database
python init_db.py

# Create tables
python setup_db.py
```

### 5. Start Development Server
```bash
# Start Flask development server
python run.py

# Or with specific configuration
python production.py
```

The API will be available at `http://localhost:5000`

### 6. Background Tasks (Optional)
```bash
# Start Celery worker (in separate terminal)
celery -A app.services.core.celery_tasks worker --loglevel=info

# Start Celery beat scheduler (in separate terminal)
celery -A app.services.core.celery_tasks beat --loglevel=info
```

## Docker Setup

### 1. Build Docker Image
```bash
docker build -t traintiq-backend .
```

### 2. Run with Docker
```bash
# Run single container
docker run -p 5000:5000 \
  -e OPENAI_API_KEY=your_key_here \
  traintiq-backend

# Run with environment file
docker run -p 5000:5000 --env-file config.env traintiq-backend
```

### 3. Docker Compose (Recommended)
```bash
# Start entire system (backend + database + redis)
docker-compose up -d

# Start only backend
docker-compose up backend

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## API Endpoints

### Health Check
```bash
GET /api/chat/health
```

### Profile Generation
```bash
POST /api/profile/generate
Content-Type: application/json

{
  "urls": ["https://example.com"],
  "custom_text": "Additional context",
  "custom_instructions": "Focus on technology stack",
  "focus_areas": ["overview", "products", "technology"],
  "use_cache": true,
  "priority": "normal"
}
```

### Chat Interface
```bash
POST /api/chat/message
Content-Type: application/json

{
  "message": "Tell me about this company",
  "context": "optional context"
}
```

### Profile Templates
```bash
GET /api/profile/templates
```

## Testing

### Unit Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_profile_generator.py

# Run with coverage
python -m pytest --cov=app tests/
```

### API Testing
```bash
# Test profile generation
python test_post.py

# Test chat API
python test_chat_api.py

# Test OpenAI integration
python test_openai.py
```

### Manual Testing
```bash
# Test profile generation endpoint
curl -X POST http://localhost:5000/api/profile/generate \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"], "custom_text": "Test company"}'

# Test health endpoint
curl http://localhost:5000/api/chat/health
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `API_PORT` | Server port | `5000` |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4-turbo-preview` |
| `DATABASE_URL` | Database connection string | Optional |
| `REDIS_URL` | Redis connection string | Optional |
| `LOG_LEVEL` | Logging level | `INFO` |

### Model Configuration
- **spaCy Model**: `en_core_web_sm` for NLP processing
- **Sentence Transformers**: `all-MiniLM-L6-v2` and `all-mpnet-base-v2` for embeddings
- **OpenAI Model**: GPT-4 Turbo for content generation

## Performance Optimization

### Caching
- Profile generation results are cached
- Vector embeddings are cached for reuse
- API responses include cache hit information

### Async Processing
- Background tasks using Celery
- Non-blocking profile generation
- Concurrent web scraping

### Resource Management
- Connection pooling for databases
- Memory-efficient text processing
- Optimized vector operations

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   ```bash
   # Verify API key
   python test_openai.py
   ```

2. **spaCy Model Missing**
   ```bash
   # Download required model
   python -m spacy download en_core_web_sm
   ```

3. **Import Errors After Reorganization**
   ```bash
   # Update import paths in your code
   from app.services.ai.chat_service import ChatService
   from app.services.data.scraping_service import ScrapingService
   from app.services.core.base_service import BaseService
   ```

4. **Database Connection Issues**
   ```bash
   # Test database connection
   python check_mysql.py
   ```

5. **Port Already in Use**
   ```bash
   # Check what's using port 5000
   netstat -an | findstr :5000
   
   # Kill process or use different port
   set API_PORT=5001
   ```

### Logging
- Application logs: `logs/app.log`
- Error logs: Console output with stack traces
- Debug mode: Set `FLASK_DEBUG=True`

### Performance Monitoring
- Profile generation timing in API responses
- Memory usage monitoring
- API response time tracking

## Development

### Adding New Services
1. Create service in appropriate directory (`ai/`, `data/`, or `core/`)
2. Inherit from `BaseService` if applicable
3. Update `__init__.py` in the service directory
4. Add tests in `tests/` directory

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Document functions and classes
- Write comprehensive tests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is proprietary software.

## Support

For technical support or questions:
- Check the troubleshooting section
- Review application logs
- Test individual components
- Verify environment configuration 