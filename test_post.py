import requests
import json

# Your dummy data
data = {
    "basicInfo": {
        "legalName": "NexusWave Technologies Inc.",
        "tradingName": "NexusWave",
        "dba": "WaveTech",
        "logoUrl": "https://placehold.co/100x100/2196F3/ffffff?text=NW",
        "foundedDate": "2015-06-15T00:00:00Z",
        "incorporationDate": "2015-05-01T00:00:00Z",
        "companyType": "private",
        "industryCodes": ["541511", "518210"]
    },
    "operational": {
        "headquarters": {
            "lat": 37.7749,
            "lng": -122.4194,
            "address": "550 Market St, San Francisco, CA 94104, USA"
        },
        "locations": [
            {
                "lat": 40.7128,
                "lng": -74.0060,
                "address": "One Liberty Plaza, New York, NY 10006, USA"
            }
        ],
        "employeeCount": 342,
        "employeeRange": "301-500",
        "operatingCountries": ["US", "CA", "GB", "DE"],
        "subsidiaries": ["WaveTech UK Ltd", "NexusWave Analytics"]
    },
    "contact": {
        "primaryPhone": "+1-415-555-0199",
        "tollFreePhone": "+1-800-555-3482",
        "email": "info@nexuswave.example",
        "investorEmail": "investors@nexuswave.example",
        "socialMedia": [
            {
                "platform": "linkedin",
                "url": "https://linkedin.com/company/nexuswave",
                "followers": 12450
            },
            {
                "platform": "twitter",
                "url": "https://twitter.com/nexuswave",
                "followers": 8765
            }
        ]
    },
    "financials": {
        "stockSymbol": "PRIVATE",
        "financialData": [
            {
                "year": 2023,
                "revenue": 48200000,
                "profit": 7500000,
                "currency": "USD"
            },
            {
                "year": 2022,
                "revenue": 38500000,
                "profit": 5200000,
                "currency": "USD"
            }
        ],
        "fundingRounds": [
            {
                "date": "2021-03-15T00:00:00Z",
                "roundType": "Series B",
                "amount": 25000000,
                "investors": ["Sequoia Capital", "Andreessen Horowitz"],
                "valuation": 180000000
            }
        ]
    },
    "descriptive": {
        "mission": "Empower businesses through intelligent data orchestration",
        "vision": "To become the operating system for enterprise data flows",
        "tagline": "The Data Fabric Company",
        "description": "NexusWave provides next-generation data integration platforms that help enterprises unify, process, and analyze data across hybrid cloud environments.",
        "coreValues": ["Innovation", "Customer Obsession", "Data Integrity", "Collaboration"],
        "keywords": ["data integration", "ETL", "cloud computing", "big data"]
    },
    "relationships": {
        "keyPeople": [
            {
                "name": "Dr. Samantha Chen",
                "title": "CEO & Co-Founder",
                "linkedinUrl": "https://linkedin.com/in/samanthachen"
            },
            {
                "name": "Raj Patel",
                "title": "CTO",
                "linkedinUrl": "https://linkedin.com/in/rajpatelcto"
            }
        ],
        "productsServices": [
            {
                "name": "WaveSync Core",
                "category": "Data Integration Platform",
                "description": "Real-time data pipeline orchestration",
                "tags": ["enterprise", "on-premise", "cloud"]
            },
            {
                "name": "WaveFlow Cloud",
                "category": "SaaS Solution",
                "description": "Fully managed data integration service",
                "launchDate": "2022-09-01T00:00:00Z"
            }
        ],
        "clients": ["Fortune 500 Retailer", "Global Bank Corp", "TechUniverse"],
        "partners": ["AWS", "Snowflake", "Databricks"],
        "competitors": ["Informatica", "Talend", "Fivetran"]
    },
    "governance": {
        "ceo": {
            "name": "Dr. Samantha Chen",
            "title": "Chief Executive Officer"
        },
        "boardMembers": [
            {
                "name": "Michael Johnson",
                "title": "Board Chair (Sequoia Capital)"
            }
        ],
        "certifications": ["SOC 2 Type II", "ISO 27001"]
    },
    "digitalPresence": {
        "websiteUrl": "https://nexuswave.example",
        "careersUrl": "https://nexuswave.example/careers",
        "techStack": ["Angular", "Node.js", "Kubernetes", "PostgreSQL"],
        "monthlyVisitors": 125000
    },
    "scrapedData": {
        "sources": [
            "https://nexuswave.example/about",
            "https://crunchbase.com/nexuswave",
            "https://linkedin.com/company/nexuswave"
        ],
        "lastScraped": "2023-11-15T14:30:00Z",
        "confidenceScore": 0.92
    },
    "metadata": {
        "lastUpdated": "2023-11-16T09:15:00Z",
        "created": "2020-01-10T10:00:00Z",
        "dataSources": ["scraped", "manual-entry"]
    },
    "customSections": {}
}

# Send POST request
url = "http://localhost:5000/api/company/"
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {str(e)}") 