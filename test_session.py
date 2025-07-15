import requests
import json

def test_session_and_loyalty():
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Test login
    login_data = {
        'email': 'test@gmail.com',
        'password': 'test123'
    }
    
    print("1. Testing login...")
    login_response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
    print(f"Login status: {login_response.status_code}")
    print(f"Login headers: {dict(login_response.headers)}")
    print(f"Login cookies: {dict(session.cookies)}")
    print(f"Login response text: {login_response.text[:200]}...")
    
    if login_response.status_code in [302, 200]:
        print("2. Testing loyalty tokens API...")
        loyalty_response = session.get('http://localhost:5000/api/loyalty_tokens')
        print(f"Loyalty API status: {loyalty_response.status_code}")
        print(f"Loyalty API response: {loyalty_response.text}")
        
        if loyalty_response.status_code == 200:
            data = loyalty_response.json()
            print(f"Found {len(data.get('tokens', []))} loyalty tokens")
            for token in data.get('tokens', []):
                print(f"  - Token ID: {token['id']}, Value: ₹{token['token_value']}")
        else:
            print("Failed to get loyalty tokens")
    else:
        print("Failed to login")

if __name__ == "__main__":
    test_session_and_loyalty() 