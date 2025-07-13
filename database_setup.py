import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def create_database():
    """Create the database and all required tables"""
    try:
        # Connect to MySQL server (without specifying database)
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                role ENUM('customer', 'admin') NOT NULL DEFAULT 'customer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create vehicles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                make VARCHAR(50) NOT NULL,
                model VARCHAR(50) NOT NULL,
                year INT NOT NULL,
                type VARCHAR(50) NOT NULL,
                base_price DECIMAL(10, 2) NOT NULL,
                availability BOOLEAN DEFAULT TRUE,
                pickup_location_lat DECIMAL(10, 8),
                pickup_location_lng DECIMAL(11, 8),
                image_url VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                vehicle_id INT NOT NULL,
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                total_price DECIMAL(10, 2) NOT NULL,
                discount_applied DECIMAL(10, 2) DEFAULT 0,
                loyalty_token_used DECIMAL(10, 2) DEFAULT 0,
                status ENUM('pending', 'approved', 'rejected', 'completed') DEFAULT 'pending',
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
            )
        """)
        
        # Create reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                booking_id INT NOT NULL,
                user_id INT NOT NULL,
                rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create pricing_rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pricing_rules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                rule_type ENUM('time_peak', 'demand_location', 'demand_car_type', 'demand_proximity') NOT NULL,
                vehicle_type VARCHAR(50),
                location_id INT,
                peak_start_time TIME,
                peak_end_time TIME,
                ramp_up_minutes INT DEFAULT 0,
                cool_down_minutes INT DEFAULT 0,
                modifier_percentage DECIMAL(5, 2) NOT NULL,
                description VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create discounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(50) UNIQUE NOT NULL,
                discount_percentage DECIMAL(5, 2) NOT NULL,
                start_date DATE,
                end_date DATE,
                vehicle_id INT,
                vehicle_type VARCHAR(50),
                usage_limit INT DEFAULT 0,
                times_used INT DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL
            )
        """)
        
        # Create loyalty_tokens table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                token_value DECIMAL(10, 2) NOT NULL,
                is_redeemed BOOLEAN DEFAULT FALSE,
                issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP,
                description VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                booking_id INT,
                user_id INT,
                amount DECIMAL(10, 2) NOT NULL,
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'success',
                method VARCHAR(50) DEFAULT 'dummy',
                reference VARCHAR(100),
                FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Insert default admin user (password: admin123)
        cursor.execute("""
            INSERT IGNORE INTO users (email, password, full_name, role) 
            VALUES ('admin@carrental.com', 'admin123', 'Admin User', 'admin')
        """)
        
        # Insert sample vehicles
        sample_vehicles = [
            # Luxury Vehicles
            ('Mercedes-Benz', 'S-Class', 2023, 'Luxury Sedan', 2500.00, True, 10.0234, 76.3112, 'https://images.pexels.com/photos/3802510/pexels-photo-3802510.jpeg'),
            ('BMW', '7 Series', 2023, 'Luxury Sedan', 2200.00, True, 10.0187, 76.3056, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg'),
            ('Audi', 'A8', 2023, 'Luxury Sedan', 2300.00, True, 10.0298, 76.3145, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg'),
            ('Range Rover', 'Sport', 2023, 'Luxury SUV', 2800.00, True, 10.0156, 76.3089, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg'),
            ('Lexus', 'LX', 2023, 'Luxury SUV', 2600.00, True, 10.0321, 76.3167, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg'),
            
            # Premium Vehicles
            ('BMW', 'X5', 2023, 'Premium SUV', 1800.00, True, 10.0267, 76.3023, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg'),
            ('Mercedes-Benz', 'GLC', 2023, 'Premium SUV', 1700.00, True, 10.0198, 76.3134, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg'),
            ('Audi', 'Q5', 2023, 'Premium SUV', 1600.00, True, 10.0345, 76.3078, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg'),
            ('Volvo', 'XC60', 2023, 'Premium SUV', 1500.00, True, 10.0212, 76.3198, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg'),
            ('Jaguar', 'F-Pace', 2023, 'Premium SUV', 1900.00, True, 10.0376, 76.3045, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg'),
            
            # Electric Vehicles
            ('Tesla', 'Model 3', 2023, 'Electric Sedan', 1200.00, True, 10.0145, 76.3212, 'https://images.pexels.com/photos/1592384/pexels-photo-1592384.jpeg'),
            ('Tesla', 'Model Y', 2023, 'Electric SUV', 1400.00, True, 10.0289, 76.3098, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg'),
            ('MG', 'ZS EV', 2023, 'Electric SUV', 800.00, True, 10.0167, 76.3156, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg'),
            ('Tata', 'Nexon EV', 2023, 'Electric SUV', 600.00, True, 10.0356, 76.3123, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg'),
            
            # Popular Sedans
            ('Honda', 'City', 2023, 'Sedan', 500.00, True, 10.0223, 76.3187, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg'),
            ('Maruti', 'Ciaz', 2023, 'Sedan', 450.00, True, 10.0312, 76.3067, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg'),
            ('Hyundai', 'Verna', 2023, 'Sedan', 480.00, True, 10.0178, 76.3245, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg'),
            ('Toyota', 'Camry', 2023, 'Sedan', 800.00, True, 10.0256, 76.3109, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg'),
            ('Skoda', 'Rapid', 2023, 'Sedan', 550.00, True, 10.0389, 76.3176, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg'),
            
            # SUVs
            ('Mahindra', 'XUV700', 2023, 'SUV', 700.00, True, 10.0134, 76.3087, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg'),
            ('Tata', 'Harrier', 2023, 'SUV', 650.00, True, 10.0298, 76.3234, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg'),
            ('MG', 'Hector', 2023, 'SUV', 750.00, True, 10.0201, 76.3165, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg'),
            ('Hyundai', 'Creta', 2023, 'SUV', 600.00, True, 10.0367, 76.3054, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg'),
            ('Kia', 'Seltos', 2023, 'SUV', 620.00, True, 10.0245, 76.3201, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg'),
            
            # Hatchbacks
            ('Maruti', 'Swift', 2023, 'Hatchback', 300.00, True, 10.0189, 76.3145, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg'),
            ('Hyundai', 'i20', 2023, 'Hatchback', 320.00, True, 10.0334, 76.3089, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg'),
            ('Tata', 'Punch', 2023, 'Hatchback', 280.00, True, 10.0156, 76.3218, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg'),
            ('Maruti', 'Baleno', 2023, 'Hatchback', 310.00, True, 10.0278, 76.3123, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg'),
            
            # Commercial Vehicles
            ('Mahindra', 'Bolero', 2023, 'Commercial', 400.00, True, 10.0301, 76.3198, 'https://images.pexels.com/photos/1118448/pexels-photo-1118448.jpeg'),
            ('Tata', 'Ace', 2023, 'Commercial', 350.00, True, 10.0167, 76.3076, 'https://images.pexels.com/photos/1118448/pexels-photo-1118448.jpeg'),
            ('Ashok Leyland', 'Dost', 2023, 'Commercial', 380.00, True, 10.0256, 76.3245, 'https://images.pexels.com/photos/1118448/pexels-photo-1118448.jpeg')
        ]
        
        cursor.executemany("""
            INSERT IGNORE INTO vehicles (make, model, year, type, base_price, availability, pickup_location_lat, pickup_location_lng, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, sample_vehicles)
        
        # Insert sample pricing rules
        sample_rules = [
            ('time_peak', None, None, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours'),
            ('demand_car_type', 'Luxury SUV', None, None, None, 0, 0, 15.00, 'High demand for luxury SUVs'),
            ('demand_car_type', 'Electric', None, None, None, 0, 0, 10.00, 'Eco-friendly premium')
        ]
        
        cursor.executemany("""
            INSERT IGNORE INTO pricing_rules (rule_type, vehicle_type, location_id, peak_start_time, peak_end_time, ramp_up_minutes, cool_down_minutes, modifier_percentage, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, sample_rules)
        
        # Insert sample discounts
        sample_discounts = [
            ('WELCOME20', 20.00, '2024-01-01', '2024-12-31', None, None, 100, 0, True),
            ('LUXURY50', 50.00, '2024-01-01', '2024-12-31', None, 'Luxury SUV', 20, 0, True),
            ('ELECTRIC15', 15.00, '2024-01-01', '2024-12-31', None, 'Electric', 50, 0, True)
        ]
        
        cursor.executemany("""
            INSERT IGNORE INTO discounts (code, discount_percentage, start_date, end_date, vehicle_id, vehicle_type, usage_limit, times_used, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, sample_discounts)
        
        conn.commit()
        print("Database and tables created successfully!")
        print("Default admin user: admin@carrental.com / admin123")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_database()