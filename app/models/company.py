from datetime import datetime
from sqlalchemy import Column, String, JSON, Text
from app import db
import json
import uuid

def generate_company_id():
    """Generate a MongoDB-style ID with timestamp and random suffix"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique = str(uuid.uuid4())[:8]
    return f"{timestamp}{unique}"

def parse_datetime(value):
    """Parse datetime from string or return as is if already datetime"""
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    return value

def datetime_to_iso(value):
    """Convert datetime to ISO format string"""
    if isinstance(value, datetime):
        return value.isoformat()
    return value

def process_json_dates(data, for_storage=False):
    """
    Recursively process JSON data to convert between datetime objects and ISO strings
    
    Args:
        data: The data to process
        for_storage: If True, converts datetime to strings. If False, converts strings to datetime.
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = process_json_dates(value, for_storage)
            elif isinstance(value, list):
                result[key] = [process_json_dates(item, for_storage) for item in value]
            elif for_storage and isinstance(value, datetime):
                result[key] = datetime_to_iso(value)
            elif not for_storage and isinstance(value, str) and any(date_field in key.lower() for date_field in ['date', 'created', 'updated', 'scraped']):
                try:
                    parsed = parse_datetime(value)
                    result[key] = parsed if parsed else value
                except (ValueError, AttributeError):
                    result[key] = value
            else:
                result[key] = value
        return result
    elif isinstance(data, list):
        return [process_json_dates(item, for_storage) for item in data]
    elif for_storage and isinstance(data, datetime):
        return datetime_to_iso(data)
    return data

class Company(db.Model):
    """Company model that matches the frontend TypeScript interface exactly"""
    __tablename__ = 'companies'

    # Use a regular id field for SQLAlchemy with auto-generation
    id = Column(String(24), primary_key=True, default=generate_company_id)
    
    # All fields are TEXT to store JSON data and be easily editable in MySQL Workbench
    basicInfo = Column(Text, nullable=True)  # Maps to BasicInfo interface
    operational = Column(Text, nullable=True)  # Maps to Operational interface
    contact = Column(Text, nullable=True)  # Maps to Contact interface
    financials = Column(Text, nullable=True)  # Maps to Financials interface
    descriptive = Column(Text, nullable=True)  # Maps to Descriptive interface
    relationships = Column(Text, nullable=True)  # Maps to Relationships interface
    governance = Column(Text, nullable=True)  # Maps to Governance interface
    digitalPresence = Column(Text, nullable=True)  # Maps to DigitalPresence interface
    scrapedData = Column(Text, nullable=True)  # Maps to ScrapedData interface
    metaInfo = Column(Text, nullable=True)  # Maps to Metadata interface
    customSections = Column(Text, nullable=True)  # Maps to customSections

    def __init__(self, **kwargs):
        """Initialize with default empty JSON objects for all fields"""
        # Remove id if provided in kwargs since we'll generate it
        kwargs.pop('id', None)
        kwargs.pop('_id', None)

        # Process any datetime fields in the input data and convert to JSON strings
        for key, value in kwargs.items():
            if isinstance(value, (dict, list)):
                processed_value = process_json_dates(value, for_storage=True)
                kwargs[key] = json.dumps(processed_value)
            elif value is None:
                kwargs[key] = '{}'

        super().__init__(**kwargs)
        # Set default empty objects for all JSON fields if not provided
        self.basicInfo = kwargs.get('basicInfo', '{}')
        self.operational = kwargs.get('operational', '{}')
        self.contact = kwargs.get('contact', '{}')
        self.financials = kwargs.get('financials', '{}')
        self.descriptive = kwargs.get('descriptive', '{}')
        self.relationships = kwargs.get('relationships', '{}')
        self.governance = kwargs.get('governance', '{}')
        self.digitalPresence = kwargs.get('digitalPresence', '{}')
        self.scrapedData = kwargs.get('scrapedData', '{}')
        self.metaInfo = kwargs.get('metaInfo', '{}')
        self.customSections = kwargs.get('customSections', '{}')

    def __repr__(self):
        """String representation of the company"""
        basic_info = json.loads(self.basicInfo) if self.basicInfo else {}
        if basic_info and basic_info.get('legalName'):
            return f"<Company {basic_info['legalName']}>"
        return "<Company Unnamed>"

    def to_dict(self):
        """Convert model to dictionary matching frontend interface"""
        return {
            "id": self.id,
            "basicInfo": process_json_dates(json.loads(self.basicInfo) if self.basicInfo else {}, for_storage=False),
            "operational": process_json_dates(json.loads(self.operational) if self.operational else {}, for_storage=False),
            "contact": process_json_dates(json.loads(self.contact) if self.contact else {}, for_storage=False),
            "financials": process_json_dates(json.loads(self.financials) if self.financials else {}, for_storage=False),
            "descriptive": process_json_dates(json.loads(self.descriptive) if self.descriptive else {}, for_storage=False),
            "relationships": process_json_dates(json.loads(self.relationships) if self.relationships else {}, for_storage=False),
            "governance": process_json_dates(json.loads(self.governance) if self.governance else {}, for_storage=False),
            "digitalPresence": process_json_dates(json.loads(self.digitalPresence) if self.digitalPresence else {}, for_storage=False),
            "scrapedData": process_json_dates(json.loads(self.scrapedData) if self.scrapedData else {}, for_storage=False),
            "metaInfo": process_json_dates(json.loads(self.metaInfo) if self.metaInfo else {}, for_storage=False),
            "customSections": process_json_dates(json.loads(self.customSections) if self.customSections else {}, for_storage=False)
        }

    @classmethod
    def from_dict(cls, data):
        """Create model instance from dictionary"""
        # Handle the metadata/meta_info mapping
        if "metadata" in data:
            data["metaInfo"] = data.pop("metadata")
            
        # Remove any ID fields from input data since we'll generate it
        data.pop('id', None)
        data.pop('_id', None)
            
        # Process any datetime fields in the input data and convert to JSON strings
        processed_data = {}
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                processed_value = process_json_dates(v, for_storage=True)
                processed_data[k] = json.dumps(processed_value)
            else:
                processed_data[k] = v
            
        # Create new instance
        return cls(**processed_data)
