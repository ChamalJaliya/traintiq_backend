from flask_restx import Api

# Initialize API with Swagger configuration
api = Api(
    title='Traintiq Scraping API',
    version='1.0',
    description='API for scraping and managing company profiles',
    doc='/swagger',
    prefix='/api'
)

# Import routes
from app.api.company_routes import api as company_namespace
from app.api.companies_routes import api as companies_namespace

# Add namespaces
api.add_namespace(company_namespace, path='/company')
api.add_namespace(companies_namespace, path='/companies')
