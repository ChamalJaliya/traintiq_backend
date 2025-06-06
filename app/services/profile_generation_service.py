from app.models.company import Company
from app import db
import logging
from datetime import date, datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileGenerationService:
    """
    Service responsible for creating or updating a Company profile
    from extracted data. Handles data mapping and type conversion.
    """
    def generate_profile(self, extracted_data: dict, company_id: int = None) -> Company:
        """
        Generates a Company object from extracted data.
        If company_id is provided, updates an existing profile; otherwise, creates a new one.
        """
        if company_id:
            company = Company.query.get(company_id)
            if not company:
                logger.warning(f"Company with ID {company_id} not found. Creating new profile.")
                company = Company()
        else:
            company = Company()

        # Map extracted data to Company fields
        # This mapping assumes 'extracted_data' keys match 'Company' attributes.
        # You might need more complex logic for fields that don't directly match or need transformation.

        # Core Information
        company.name = extracted_data.get('name') or company.name # Use extracted or keep existing
        company.website_url = extracted_data.get('website_url') or company.website_url
        company.industry = extracted_data.get('industry') or company.industry
        company.description = extracted_data.get('description') or company.description
        company.legal_status = extracted_data.get('legal_status') or company.legal_status

        # Date conversion (example)
        founding_date_str = extracted_data.get('founding_date')
        if founding_date_str:
            try:
                # Assuming 'YYYY' format from extraction. Adjust if different.
                company.founding_date = date(int(founding_date_str), 1, 1) # Set to Jan 1st of that year
            except ValueError:
                logger.warning(f"Could not parse founding date: {founding_date_str}")
                company.founding_date = None # Set to None on failure

        # Contact Information
        company.address = extracted_data.get('address') or company.address
        company.phone_number = extracted_data.get('phone_number') or company.phone_number
        company.email = extracted_data.get('email') or company.email
        company.social_media_links = extracted_data.get('social_media_links') or company.social_media_links

        # Business Metrics & Details
        company.employee_count = extracted_data.get('employee_count') or company.employee_count
        company.revenue_range = extracted_data.get('revenue_range') or company.revenue_range
        company.products_services = extracted_data.get('products_services') or company.products_services
        company.mission_statement = extracted_data.get('mission_statement') or company.mission_statement
        company.vision_statement = extracted_data.get('vision_statement') or company.vision_statement
        company.values = extracted_data.get('values') or company.values

        # Key Personnel / Leadership
        company.key_personnel = extracted_data.get('key_personnel') or company.key_personnel

        # Certifications and Awards
        company.certifications = extracted_data.get('certifications') or company.certifications
        company.awards = extracted_data.get('awards') or company.awards

        # News & Media
        company.recent_news_links = extracted_data.get('recent_news_links') or company.recent_news_links

        # SEO/Keywords
        company.keywords = extracted_data.get('keywords') or company.keywords

        try:
            if company._id: # If updating
                db.session.merge(company) # Use merge for updates or add for new
            else: # If creating
                db.session.add(company)
            db.session.commit()
            logger.info(f"Company profile '{company.name}' (ID: {company._id}) saved/updated successfully.")
            return company
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving/updating company profile: {e}")
            raise RuntimeError(f"Database error during profile generation: {e}")
