from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.core.base_service import BaseService
from app.models.company import Company
from app.repositories.company_repository import CompanyRepository
from app.dto.company_dto import (
    CreateCompanyDTO,
    UpdateCompanyDTO,
    ScrapeCompanyDTO,
    CompanySize
)
from app.exceptions import ValidationException, NotFoundException
from app.services.data.scraping_service import ScrapingService
from app.services.data.data_extraction_service import DataExtractionService

class CompanyService(BaseService[Company, CreateCompanyDTO, UpdateCompanyDTO, CreateCompanyDTO]):
    def __init__(self):
        self.repository = CompanyRepository()
        self.scraping_service = ScrapingService()
        self.data_extraction_service = DataExtractionService()
        super().__init__(self.repository, CreateCompanyDTO)

    async def validate_company_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate company data before creation or update
        Raises ValidationException if validation fails
        """
        # Validate company name
        if 'name' in data and not data['name'].strip():
            raise ValidationException("Company name cannot be empty")

        # Validate employee count
        if 'employee_count' in data and data['employee_count'] is not None:
            if not isinstance(data['employee_count'], int) or data['employee_count'] < 0:
                raise ValidationException("Employee count must be a positive integer")

        # Validate company size
        if 'company_size' in data and data['company_size'] is not None:
            try:
                CompanySize(data['company_size'])
            except ValueError:
                raise ValidationException(f"Invalid company size. Must be one of: {', '.join(CompanySize.__members__)}")

        # Validate dates
        if 'founding_date' in data and data['founding_date'] is not None:
            try:
                if isinstance(data['founding_date'], str):
                    datetime.strptime(data['founding_date'], '%Y-%m-%d')
            except ValueError:
                raise ValidationException("Invalid founding date format. Use YYYY-MM-DD")

        # Validate email
        if 'email' in data and data['email'] is not None:
            if '@' not in data['email']:
                raise ValidationException("Invalid email format")

        return True

    async def create_company(self, dto: CreateCompanyDTO) -> CreateCompanyDTO:
        """Create a new company with validation"""
        data = dto.model_dump(exclude_unset=True)
        await self.validate_company_data(data)
        return await super().create(dto)

    async def update_company(self, id: int, dto: UpdateCompanyDTO) -> CreateCompanyDTO:
        """Update an existing company with validation"""
        data = dto.model_dump(exclude_unset=True)
        await self.validate_company_data(data)
        return await super().update(id, dto)

    async def scrape_company(self, dto: ScrapeCompanyDTO) -> CreateCompanyDTO:
        """Scrape company information from multiple URLs and documents"""
        all_content = []
        scraping_sources = []
        
        # Scrape all provided URLs
        for url in dto.urls:
            try:
                html_content = await self.scraping_service.scrape_website(str(url))
                all_content.append(html_content)
                scraping_sources.append(str(url))
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
                # Continue with other URLs even if one fails
                continue
        
        # Add document content if provided
        if dto.documentContent and dto.documentNames:
            for i, content in enumerate(dto.documentContent):
                all_content.append(content)
                doc_name = dto.documentNames[i] if i < len(dto.documentNames) else f"document_{i+1}"
                scraping_sources.append(f"uploaded_document: {doc_name}")
        
        # Combine all content
        combined_content = "\n\n--- CONTENT SEPARATOR ---\n\n".join(all_content)
        
        # Extract data with custom instructions
        extracted_data = await self.data_extraction_service.extract_company_data(
            combined_content,
            custom_instructions=dto.customInstructions,
            data_sources=scraping_sources
        )
        
        # Add metadata about sources
        if 'scrapedData' not in extracted_data:
            extracted_data['scrapedData'] = {}
        
        extracted_data['scrapedData']['sources'] = scraping_sources
        extracted_data['scrapedData']['lastScraped'] = datetime.now()
        extracted_data['scrapedData']['contentSources'] = len(all_content)
        
        # Create new company profile
        create_dto = CreateCompanyDTO(**extracted_data)
        return await self.create_company(create_dto)

    def search_companies(
        self,
        query: Optional[str] = None,
        industry: Optional[str] = None,
        min_employees: Optional[int] = None,
        max_employees: Optional[int] = None,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = 10
    ) -> List[CreateCompanyDTO]:
        """
        Advanced search for companies with multiple criteria
        """
        companies = []

        if query:
            companies.extend(self.repository.search_companies(query))
        
        if industry:
            industry_companies = self.repository.get_companies_by_industry(industry)
            companies.extend(company for company in industry_companies if company not in companies)

        if min_employees is not None and max_employees is not None:
            employee_companies = self.repository.get_by_employee_count(min_employees, max_employees)
            companies.extend(company for company in employee_companies if company not in companies)

        if any([country, state, city]):
            location_companies = self.repository.get_by_location(country, state, city)
            companies.extend(company for company in location_companies if company not in companies)

        # If no filters applied, get recently updated companies
        if not companies:
            companies = self.repository.get_recently_updated(limit=limit)

        # Convert to DTOs and return
        return [self._to_response_dto(company) for company in companies[:limit]] 