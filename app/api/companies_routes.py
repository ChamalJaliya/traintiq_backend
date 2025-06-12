from flask import Blueprint
from flask_restx import Resource, Namespace, fields, Api
from app.services.core.company_service import CompanyService
from app.schemas.company_schema import CompanyProfileSchema
from app.exceptions import ValidationException, DatabaseException
from app import db

# Create Blueprint and API namespace
companies_bp = Blueprint('companies_bp', __name__)
api = Namespace('companies', description='Multiple companies operations')

# Initialize schemas and services
companies_schema = CompanyProfileSchema(many=True)
company_service = CompanyService()

# Import the company profile model from company_routes
from app.api.company_routes import company_profile

# Search filters model
search_filters = api.model('SearchFilters', {
    'query': fields.String(description='Search query for company name, description, etc.'),
    'industry': fields.String(description='Industry filter'),
    'min_employees': fields.Integer(description='Minimum number of employees'),
    'max_employees': fields.Integer(description='Maximum number of employees'),
    'country': fields.String(description='Country filter'),
    'state': fields.String(description='State/Province filter'),
    'city': fields.String(description='City filter'),
    'limit': fields.Integer(description='Maximum number of results to return', default=10)
})

@api.route('/')
class CompaniesList(Resource):
    @api.doc('list_companies')
    @api.marshal_list_with(company_profile)
    async def get(self):
        """List all companies"""
        try:
            return await company_service.get_all()
        except Exception as e:
            api.abort(500, str(e))

@api.route('/search')
class CompaniesSearch(Resource):
    @api.doc('search_companies')
    @api.expect(search_filters)
    @api.marshal_list_with(company_profile)
    async def post(self):
        """Search companies with filters"""
        try:
            return await company_service.search_companies(**api.payload)
        except ValidationException as e:
            api.abort(400, str(e))
        except DatabaseException as e:
            api.abort(500, str(e))

@api.route('/db/reset')
class DatabaseOperations(Resource):
    @api.doc('reset_database')
    @api.response(200, 'Database reset successfully')
    @api.response(500, 'Database error')
    def post(self):
        """Drop all data from the database and recreate tables"""
        try:
            # Drop all tables
            db.drop_all()
            # Recreate all tables
            db.create_all()
            return {'message': 'Database reset successfully', 'status': 'success'}, 200
        except Exception as e:
            return {'message': f'Database error: {str(e)}', 'status': 'error'}, 500 