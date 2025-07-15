import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def check_discounts():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM discounts')
        discounts = cursor.fetchall()
        
        print('Available discounts:')
        if discounts:
            for discount in discounts:
                print(f'Code: {discount["code"]}, Percentage: {discount["discount_percentage"]}%, Type: {discount["vehicle_type"]}, Active: {discount["is_active"]}, Description: {discount.get("description", "N/A")}')
        else:
            print('No discounts found in database')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_discounts() 