import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def check_vehicles():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT id, make, model, type, base_price FROM vehicles LIMIT 10')
        vehicles = cursor.fetchall()
        
        print('Available vehicles:')
        for vehicle in vehicles:
            print(f'ID: {vehicle["id"]}, {vehicle["make"]} {vehicle["model"]} ({vehicle["type"]}) - ₹{vehicle["base_price"]}/hour')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_vehicles() 