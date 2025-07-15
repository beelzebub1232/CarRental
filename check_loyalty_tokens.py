import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def check_loyalty_tokens():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM loyalty_tokens')
        tokens = cursor.fetchall()
        
        print('Available loyalty tokens:')
        if tokens:
            for token in tokens:
                print(f'ID: {token["id"]}, User ID: {token["user_id"]}, Value: ₹{token["token_value"]}, Redeemed: {token["is_redeemed"]}, Expiry: {token["expiry_date"]}, Description: {token.get("description", "N/A")}')
        else:
            print('No loyalty tokens found in database')
        
        # Also check users table to see available users
        cursor.execute('SELECT id, email, full_name FROM users')
        users = cursor.fetchall()
        print(f'\nAvailable users:')
        for user in users:
            print(f'ID: {user["id"]}, Email: {user["email"]}, Name: {user["full_name"]}')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    check_loyalty_tokens() 