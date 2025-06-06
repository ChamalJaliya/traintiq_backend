from marshmallow import fields, Schema, post_dump, pre_load
from app import ma
from app.models.company import Company
from datetime import datetime

def parse_datetime(value):
    """Parse datetime from string or return as is if already datetime"""
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    return value

class DateTimeField(fields.DateTime):
    """Custom DateTime field that can handle both datetime objects and ISO format strings"""
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str):
            return parse_datetime(value)
        return super()._deserialize(value, attr, data, **kwargs)

class GeoLocationSchema(Schema):
    lat = fields.Float(allow_none=True)
    lng = fields.Float(allow_none=True)
    address = fields.String(allow_none=True)

class SocialMediaProfileSchema(Schema):
    platform = fields.String(allow_none=True)
    url = fields.String(allow_none=True)
    followers = fields.Integer(allow_none=True)

class FinancialYearDataSchema(Schema):
    year = fields.Integer(allow_none=True)
    revenue = fields.Float(allow_none=True)
    profit = fields.Float(allow_none=True)
    currency = fields.String(allow_none=True)

class FundingRoundSchema(Schema):
    date = DateTimeField(format='iso', allow_none=True)
    roundType = fields.String(allow_none=True)
    amount = fields.Float(allow_none=True)
    investors = fields.List(fields.String(), allow_none=True)
    valuation = fields.Float(allow_none=True)

class KeyPersonSchema(Schema):
    name = fields.String(allow_none=True)
    title = fields.String(allow_none=True)
    linkedinUrl = fields.String(allow_none=True)

class ProductServiceSchema(Schema):
    name = fields.String(allow_none=True)
    category = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    tags = fields.List(fields.String(), allow_none=True)
    launchDate = DateTimeField(format='iso', allow_none=True)

class BoardMemberSchema(Schema):
    name = fields.String(allow_none=True)
    title = fields.String(allow_none=True)

class BasicInfoSchema(Schema):
    legalName = fields.String(allow_none=True)
    tradingName = fields.String(allow_none=True)
    dba = fields.String(allow_none=True)
    logoUrl = fields.String(allow_none=True)
    foundedDate = DateTimeField(format='iso', allow_none=True)
    incorporationDate = DateTimeField(format='iso', allow_none=True)
    companyType = fields.String(allow_none=True)
    industryCodes = fields.List(fields.String(), allow_none=True)

class OperationalSchema(Schema):
    headquarters = fields.Nested(GeoLocationSchema, allow_none=True)
    locations = fields.List(fields.Nested(GeoLocationSchema), allow_none=True)
    employeeCount = fields.Integer(allow_none=True)
    employeeRange = fields.String(allow_none=True)
    operatingCountries = fields.List(fields.String(), allow_none=True)
    subsidiaries = fields.List(fields.String(), allow_none=True)

class ContactSchema(Schema):
    primaryPhone = fields.String(allow_none=True)
    tollFreePhone = fields.String(allow_none=True)
    email = fields.String(allow_none=True)
    investorEmail = fields.String(allow_none=True)
    socialMedia = fields.List(fields.Nested(SocialMediaProfileSchema), allow_none=True)

class FinancialsSchema(Schema):
    stockSymbol = fields.String(allow_none=True)
    financialData = fields.List(fields.Nested(FinancialYearDataSchema), allow_none=True)
    fundingRounds = fields.List(fields.Nested(FundingRoundSchema), allow_none=True)

class DescriptiveSchema(Schema):
    mission = fields.String(allow_none=True)
    vision = fields.String(allow_none=True)
    tagline = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    coreValues = fields.List(fields.String(), allow_none=True)
    keywords = fields.List(fields.String(), allow_none=True)

class RelationshipsSchema(Schema):
    keyPeople = fields.List(fields.Nested(KeyPersonSchema), allow_none=True)
    productsServices = fields.List(fields.Nested(ProductServiceSchema), allow_none=True)
    clients = fields.List(fields.String(), allow_none=True)
    partners = fields.List(fields.String(), allow_none=True)
    competitors = fields.List(fields.String(), allow_none=True)

class GovernanceSchema(Schema):
    ceo = fields.Dict(allow_none=True)
    boardMembers = fields.List(fields.Nested(BoardMemberSchema), allow_none=True)
    certifications = fields.List(fields.String(), allow_none=True)

class DigitalPresenceSchema(Schema):
    websiteUrl = fields.String(allow_none=True)
    careersUrl = fields.String(allow_none=True)
    techStack = fields.List(fields.String(), allow_none=True)
    monthlyVisitors = fields.Integer(allow_none=True)

class ScrapedDataSchema(Schema):
    sources = fields.List(fields.String(), allow_none=True)
    lastScraped = DateTimeField(format='iso', allow_none=True)
    confidenceScore = fields.Float(allow_none=True)

class MetaInfoSchema(Schema):
    lastUpdated = DateTimeField(format='iso', allow_none=True)
    created = DateTimeField(format='iso', allow_none=True)
    dataSources = fields.List(fields.String(), allow_none=True)

class CompanyProfileSchema(ma.SQLAlchemyAutoSchema):
    """
    Marshmallow schema for serializing and deserializing Company objects.
    Matches the frontend TypeScript interface exactly.
    """
    class Meta:
        model = Company
        load_instance = True
        include_fk = True
        # Include all fields
        fields = ('id', 'basicInfo', 'operational', 'contact', 'financials',
                 'descriptive', 'relationships', 'governance', 'digitalPresence',
                 'scrapedData', 'metaInfo', 'customSections')

    # Define all nested fields
    basicInfo = fields.Nested(BasicInfoSchema, allow_none=True)
    operational = fields.Nested(OperationalSchema, allow_none=True)
    contact = fields.Nested(ContactSchema, allow_none=True)
    financials = fields.Nested(FinancialsSchema, allow_none=True)
    descriptive = fields.Nested(DescriptiveSchema, allow_none=True)
    relationships = fields.Nested(RelationshipsSchema, allow_none=True)
    governance = fields.Nested(GovernanceSchema, allow_none=True)
    digitalPresence = fields.Nested(DigitalPresenceSchema, allow_none=True)
    scrapedData = fields.Nested(ScrapedDataSchema, allow_none=True)
    metaInfo = fields.Nested(MetaInfoSchema, allow_none=True)
    customSections = fields.Dict(allow_none=True)

    @post_dump
    def rename_id(self, data, **kwargs):
        """Convert _id to id in the output"""
        if '_id' in data:
            data['id'] = data.pop('_id')
        return data
