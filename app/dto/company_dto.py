from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, HttpUrl, EmailStr, constr, validator, Field
from enum import Enum

class CompanySize(str, Enum):
    MICRO = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "201-1000"
    ENTERPRISE = "1000+"

class SocialMediaLinks(BaseModel):
    linkedin: Optional[HttpUrl]
    twitter: Optional[HttpUrl]
    facebook: Optional[HttpUrl]
    instagram: Optional[HttpUrl]
    youtube: Optional[HttpUrl]

class KeyPerson(BaseModel):
    """Interface for a key person within the company"""
    name: str
    title: str
    linkedinUrl: Optional[str] = None

class Award(BaseModel):
    name: str
    year: int
    description: Optional[str]
    issuer: Optional[str]

class NewsLink(BaseModel):
    title: str
    url: HttpUrl
    date: Optional[date]
    source: Optional[str]

class GeoLocation(BaseModel):
    """Interface for geographical location data"""
    lat: float
    lng: float
    address: str

class SocialMediaProfile(BaseModel):
    """Interface for a company's social media profile"""
    platform: str
    url: str
    followers: Optional[int] = None

class FinancialYearData(BaseModel):
    """Interface for a single year's financial data"""
    year: int
    revenue: float
    profit: float
    currency: str

class FundingRound(BaseModel):
    """Interface for a company's funding round details"""
    date: datetime
    roundType: str
    amount: float
    investors: List[str]
    valuation: Optional[float] = None

class ProductService(BaseModel):
    """Interface for a product or service offered by the company"""
    name: str
    category: str
    description: str
    tags: Optional[List[str]] = None
    launchDate: Optional[datetime] = None

class BoardMember(BaseModel):
    """Interface for a board member"""
    name: str
    title: str

class BasicInfo(BaseModel):
    """Basic identifying information about the company"""
    legalName: str
    tradingName: Optional[str] = None
    dba: Optional[str] = None
    logoUrl: Optional[str] = None
    foundedDate: Optional[datetime] = None
    incorporationDate: Optional[datetime] = None
    companyType: Optional[str] = None
    industryCodes: Optional[List[str]] = None

class Operational(BaseModel):
    """Operational details of the company"""
    headquarters: Optional[GeoLocation] = None
    locations: Optional[List[GeoLocation]] = None
    employeeCount: Optional[int] = None
    employeeRange: Optional[str] = None
    operatingCountries: Optional[List[str]] = None
    subsidiaries: Optional[List[str]] = None

class Contact(BaseModel):
    """Contact information for the company"""
    primaryPhone: Optional[str] = None
    tollFreePhone: Optional[str] = None
    email: Optional[str] = None
    investorEmail: Optional[str] = None
    socialMedia: Optional[List[SocialMediaProfile]] = None

class Financials(BaseModel):
    """Financial overview and history of the company"""
    stockSymbol: Optional[str] = None
    financialData: Optional[List[FinancialYearData]] = None
    fundingRounds: Optional[List[FundingRound]] = None

class Descriptive(BaseModel):
    """Descriptive information about the company's purpose and identity"""
    mission: Optional[str] = None
    vision: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    coreValues: Optional[List[str]] = None
    keywords: Optional[List[str]] = None

class Relationships(BaseModel):
    """Relationships with key individuals, offerings, clients, partners, and competitors"""
    keyPeople: Optional[List[KeyPerson]] = None
    productsServices: Optional[List[ProductService]] = None
    clients: Optional[List[str]] = None
    partners: Optional[List[str]] = None
    competitors: Optional[List[str]] = None

class Governance(BaseModel):
    """Information related to company leadership and compliance"""
    ceo: Optional[Dict[str, str]] = None
    boardMembers: Optional[List[BoardMember]] = None
    certifications: Optional[List[str]] = None

class DigitalPresence(BaseModel):
    """Details about the company's online and digital presence"""
    websiteUrl: Optional[str] = None
    careersUrl: Optional[str] = None
    techStack: Optional[List[str]] = None
    monthlyVisitors: Optional[int] = None

class ScrapedData(BaseModel):
    """Information about the data source, particularly if scraped"""
    sources: Optional[List[str]] = None
    lastScraped: Optional[datetime] = None
    confidenceScore: Optional[float] = None

class Metadata(BaseModel):
    """General metadata about the profile record itself"""
    lastUpdated: Optional[datetime] = None
    created: Optional[datetime] = None
    dataSources: Optional[List[str]] = None

class CompanyProfileBase(BaseModel):
    """Base model for company profiles"""
    _id: Optional[str] = None
    basicInfo: Optional[BasicInfo] = None
    operational: Optional[Operational] = None
    contact: Optional[Contact] = None
    financials: Optional[Financials] = None
    descriptive: Optional[Descriptive] = None
    relationships: Optional[Relationships] = None
    governance: Optional[Governance] = None
    digitalPresence: Optional[DigitalPresence] = None
    scrapedData: Optional[ScrapedData] = None
    metadata: Optional[Metadata] = None
    customSections: Optional[Dict[str, Any]] = None

class CreateCompanyDTO(CompanyProfileBase):
    """DTO for creating a new company profile"""
    pass

class UpdateCompanyDTO(CompanyProfileBase):
    """DTO for updating an existing company profile"""
    pass

class CompanyProfileResponseDTO(CompanyProfileBase):
    """DTO for company profile responses"""
    class Config:
        from_attributes = True

class ProfileGenerationRequest(BaseModel):
    """Request payload for generating a company profile"""
    url: str
    customInstructions: Optional[str] = None

class ScrapeCompanyDTO(BaseModel):
    """DTO for company scraping requests"""
    url: HttpUrl
    customInstructions: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "customInstructions": None
            }
        } 