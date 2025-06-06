from app import create_app, db
from app.models.company import Company

def view_companies():
    app = create_app()
    with app.app_context():
        companies = Company.query.all()
        print(f"\nFound {len(companies)} companies in database:")
        for company in companies:
            print(f"\nCompany ID: {company._id}")
            if company.basicInfo and 'legalName' in company.basicInfo:
                print(f"Name: {company.basicInfo['legalName']}")
            print("-" * 50)

if __name__ == "__main__":
    view_companies() 