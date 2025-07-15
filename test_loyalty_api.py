import requests
import json

def test_loyalty_api():
    # Test the loyalty tokens API endpoint
    try:
        # First, we need to login to get a session
        session = requests.Session()
        
        # Login as a test user (you may need to adjust the credentials)
        login_data = {
            'email': 'test@gmail.com',
            'password': 'test123'
        }
        
        login_response = session.post('http://localhost:5000/login', data=login_data)
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            # Now test the loyalty tokens API
            loyalty_response = session.get('http://localhost:5000/api/loyalty_tokens')
            print(f"Loyalty API response status: {loyalty_response.status_code}")
            print(f"Loyalty API response: {loyalty_response.text}")
            
            if loyalty_response.status_code == 200:
                data = loyalty_response.json()
                print(f"Tokens found: {len(data.get('tokens', []))}")
                for token in data.get('tokens', []):
                    print(f"Token: {token}")
            else:
                print("Failed to get loyalty tokens")
        else:
            print("Failed to login")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_loyalty_api() 