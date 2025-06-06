import requests
import json

def reset_database():
    """Reset the database by dropping and recreating all tables"""
    url = "http://localhost:5000/api/companies/db/reset"
    try:
        response = requests.post(url)
        print(f"Status Code: {response.status_code}")
        
        try:
            result = response.json()
            print("\nResponse:")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Message: {result.get('message', 'No message provided')}")
        except json.JSONDecodeError:
            print("\nRaw Response:")
            print(response.text)
            
    except requests.RequestException as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    reset_database() 