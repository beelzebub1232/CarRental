from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, SECRET_KEY, DEBUG
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['DEBUG'] = DEBUG

def get_db_connection():
    """Get database connection"""
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return conn

def calculate_final_price(vehicle_id, start_datetime, end_datetime):
    """Calculate final price with dynamic pricing rules"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get vehicle details
        cursor.execute("SELECT base_price, type FROM vehicles WHERE id = %s", (vehicle_id,))
        vehicle = cursor.fetchone()
        if not vehicle:
            return None
        
        base_price = float(vehicle['base_price'])
        vehicle_type = vehicle['type']
        
        # Calculate duration in hours
        duration_hours = (end_datetime - start_datetime).total_seconds() / 3600
        calculated_price = base_price * duration_hours
        
        # Apply time-based peak modifiers
        cursor.execute("SELECT * FROM pricing_rules WHERE rule_type = 'time_peak' AND is_active = TRUE")
        time_rules = cursor.fetchall()
        
        for rule in time_rules:
            peak_start = rule['peak_start_time']
            peak_end = rule['peak_end_time']
            booking_time = start_datetime.time()
            
            if peak_start <= booking_time <= peak_end:
                calculated_price *= (1 + float(rule['modifier_percentage']) / 100)
        
        # Apply demand-based modifiers for car type
        cursor.execute(
            "SELECT modifier_percentage FROM pricing_rules WHERE rule_type = 'demand_car_type' AND vehicle_type = %s AND is_active = TRUE",
            (vehicle_type,)
        )
        demand_rule = cursor.fetchone()
        if demand_rule:
            calculated_price *= (1 + float(demand_rule['modifier_percentage']) / 100)
        
        return round(calculated_price, 2)
        
    finally:
        cursor.close()
        conn.close()

# Authentication routes
@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('customer_dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid email or password')
        
        cursor.close()
        conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (email, password, full_name, role) VALUES (%s, %s, %s, 'customer')",
                (email, password, full_name)
            )
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Email already exists')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Customer routes
@app.route('/customer/dashboard')
def customer_dashboard():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get recent bookings
    cursor.execute("""
        SELECT b.*, v.make, v.model, v.year, v.type, v.image_url
        FROM bookings b
        JOIN vehicles v ON b.vehicle_id = v.id
        WHERE b.user_id = %s
        ORDER BY b.booking_date DESC
        LIMIT 5
    """, (session['user_id'],))
    recent_bookings = cursor.fetchall()
    
    # Get loyalty tokens
    cursor.execute("""
        SELECT * FROM loyalty_tokens 
        WHERE user_id = %s AND is_redeemed = FALSE AND (expiry_date IS NULL OR expiry_date > NOW())
        ORDER BY issued_date DESC
    """, (session['user_id'],))
    loyalty_tokens = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('customer/dashboard.html', 
                         recent_bookings=recent_bookings, 
                         loyalty_tokens=loyalty_tokens)

@app.route('/customer/booking')
def customer_booking():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM vehicles WHERE availability = TRUE ORDER BY make, model")
    vehicles = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('customer/booking.html', vehicles=vehicles)

@app.route('/customer/profile')
def customer_profile():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user details
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    # Get all bookings
    cursor.execute("""
        SELECT b.*, v.make, v.model, v.year, v.type
        FROM bookings b
        JOIN vehicles v ON b.vehicle_id = v.id
        WHERE b.user_id = %s
        ORDER BY b.booking_date DESC
    """, (session['user_id'],))
    bookings = cursor.fetchall()
    
    # Get loyalty tokens history
    cursor.execute("""
        SELECT * FROM loyalty_tokens 
        WHERE user_id = %s
        ORDER BY issued_date DESC
    """, (session['user_id'],))
    loyalty_tokens = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('customer/profile.html', 
                         user=user, 
                         bookings=bookings, 
                         loyalty_tokens=loyalty_tokens)

# Admin routes
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get dashboard statistics
    cursor.execute("SELECT COUNT(*) as total FROM vehicles")
    total_vehicles = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'customer'")
    total_customers = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM bookings WHERE status = 'pending'")
    pending_bookings = cursor.fetchone()['total']
    
    cursor.execute("SELECT SUM(total_price) as total FROM bookings WHERE status = 'completed'")
    total_revenue = cursor.fetchone()['total'] or 0
    
    # Get recent bookings
    cursor.execute("""
        SELECT b.*, u.full_name, v.make, v.model
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN vehicles v ON b.vehicle_id = v.id
        ORDER BY b.booking_date DESC
        LIMIT 10
    """)
    recent_bookings = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/dashboard.html',
                         total_vehicles=total_vehicles,
                         total_customers=total_customers,
                         pending_bookings=pending_bookings,
                         total_revenue=total_revenue,
                         recent_bookings=recent_bookings)

@app.route('/admin/manage_vehicles')
def admin_manage_vehicles():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM vehicles ORDER BY make, model")
    vehicles = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/manage_vehicles.html', vehicles=vehicles)

@app.route('/admin/reports')
def admin_reports():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get booking statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_bookings,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_bookings,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_bookings,
            SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_bookings,
            SUM(total_price) as total_revenue
        FROM bookings
    """)
    stats = cursor.fetchone()
    
    # Get popular vehicles
    cursor.execute("""
        SELECT v.make, v.model, v.type, COUNT(b.id) as booking_count
        FROM vehicles v
        LEFT JOIN bookings b ON v.id = b.vehicle_id
        GROUP BY v.id
        ORDER BY booking_count DESC
        LIMIT 10
    """)
    popular_vehicles = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/reports.html', stats=stats, popular_vehicles=popular_vehicles)

# API routes
@app.route('/api/calculate_price', methods=['POST'])
def api_calculate_price():
    data = request.get_json()
    vehicle_id = data.get('vehicle_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    try:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
        
        price = calculate_final_price(vehicle_id, start_datetime, end_datetime)
        
        return jsonify({'price': price})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/create_booking', methods=['POST'])
def api_create_booking():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    vehicle_id = data.get('vehicle_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    discount_code = data.get('discount_code', '')
    loyalty_token_id = data.get('loyalty_token_id')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
        
        # Calculate base price
        total_price = calculate_final_price(vehicle_id, start_datetime, end_datetime)
        discount_applied = 0
        loyalty_token_used = 0
        
        # Apply discount code if provided
        if discount_code:
            cursor.execute("""
                SELECT * FROM discounts 
                WHERE code = %s AND is_active = TRUE 
                AND start_date <= CURDATE() AND end_date >= CURDATE()
                AND (usage_limit = 0 OR times_used < usage_limit)
            """, (discount_code,))
            discount = cursor.fetchone()
            
            if discount:
                discount_applied = total_price * (float(discount['discount_percentage']) / 100)
                total_price -= discount_applied
                
                # Update discount usage
                cursor.execute(
                    "UPDATE discounts SET times_used = times_used + 1 WHERE id = %s",
                    (discount['id'],)
                )
        
        # Apply loyalty token if provided
        if loyalty_token_id:
            cursor.execute("""
                SELECT * FROM loyalty_tokens 
                WHERE id = %s AND user_id = %s AND is_redeemed = FALSE
                AND (expiry_date IS NULL OR expiry_date > NOW())
            """, (loyalty_token_id, session['user_id']))
            token = cursor.fetchone()
            
            if token:
                loyalty_token_used = min(float(token['token_value']), total_price)
                total_price -= loyalty_token_used
                
                # Mark token as redeemed
                cursor.execute(
                    "UPDATE loyalty_tokens SET is_redeemed = TRUE WHERE id = %s",
                    (loyalty_token_id,)
                )
        
        # Create booking
        cursor.execute("""
            INSERT INTO bookings 
            (user_id, vehicle_id, start_date, end_date, total_price, discount_applied, loyalty_token_used)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], vehicle_id, start_datetime, end_datetime, 
              total_price, discount_applied, loyalty_token_used))
        
        booking_id = cursor.lastrowid
        
        # Issue loyalty token (5% of booking value)
        loyalty_value = total_price * 0.05
        expiry_date = datetime.now() + timedelta(days=365)
        
        cursor.execute("""
            INSERT INTO loyalty_tokens (user_id, token_value, expiry_date, description)
            VALUES (%s, %s, %s, %s)
        """, (session['user_id'], loyalty_value, expiry_date, f'Earned from booking #{booking_id}'))
        
        conn.commit()
        
        return jsonify({
            'success': True, 
            'booking_id': booking_id,
            'total_price': total_price,
            'loyalty_earned': loyalty_value
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/simulate_price', methods=['POST'])
def admin_simulate_price():
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    vehicle_id = data.get('vehicle_id')
    start_str = data.get('start_datetime')
    end_str = data.get('end_datetime')
    
    try:
        start_datetime = datetime.strptime(start_str, '%Y-%m-%dT%H:%M')
        end_datetime = datetime.strptime(end_str, '%Y-%m-%dT%H:%M')
        
        simulated_price = calculate_final_price(vehicle_id, start_datetime, end_datetime)
        
        return jsonify({'simulated_price': simulated_price})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=DEBUG)