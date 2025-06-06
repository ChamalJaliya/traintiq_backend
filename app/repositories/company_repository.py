from typing import Optional, List
from datetime import datetime
from sqlalchemy import or_
from app.repositories.base_repository import BaseRepository
from app.models.company import Company
from app.dto.company_dto import CreateCompanyDTO, UpdateCompanyDTO

class CompanyRepository(BaseRepository[Company]):
    def __init__(self):
        super().__init__(Company)

    def create_from_dto(self, dto: CreateCompanyDTO) -> Company:
        """Create a company from DTO"""
        company_data = dto.model_dump(exclude_unset=True)
        return self.create(**company_data)

    def update_from_dto(self, company: Company, dto: UpdateCompanyDTO) -> Company:
        """Update a company from DTO"""
        update_data = dto.model_dump(exclude_unset=True)
        return self.update(company, **update_data)

    def search_companies(self, query: str) -> List[Company]:
        """Search companies by name, description, or industry"""
        return self.model.query.filter(
            or_(
                self.model.name.ilike(f"%{query}%"),
                self.model.description.ilike(f"%{query}%"),
                self.model.industry.ilike(f"%{query}%")
            )
        ).all()

    def get_companies_by_industry(self, industry: str) -> List[Company]:
        """Get all companies in a specific industry"""
        return self.find_by(industry=industry)

    def get_recently_updated(self, limit: int = 10) -> List[Company]:
        """Get recently updated companies"""
        return self.model.query.order_by(
            self.model.updated_at.desc()
        ).limit(limit).all()

    def get_by_revenue_range(self, min_revenue: str, max_revenue: str) -> List[Company]:
        """Get companies within a specific revenue range"""
        return self.model.query.filter(
            self.model.revenue_range.between(min_revenue, max_revenue)
        ).all()

    def get_by_employee_count(self, min_count: int, max_count: int) -> List[Company]:
        """Get companies within an employee count range"""
        return self.model.query.filter(
            self.model.employee_count.between(min_count, max_count)
        ).all()

    def get_by_founding_date_range(self, start_date: datetime, end_date: datetime) -> List[Company]:
        """Get companies founded within a date range"""
        return self.model.query.filter(
            self.model.founding_date.between(start_date, end_date)
        ).all()

    def get_by_location(self, country: Optional[str] = None, state: Optional[str] = None, 
                       city: Optional[str] = None) -> List[Company]:
        """Get companies by location"""
        query = self.model.query
        if country:
            query = query.filter(self.model.country == country)
        if state:
            query = query.filter(self.model.state_province == state)
        if city:
            query = query.filter(self.model.city == city)
        return query.all() 