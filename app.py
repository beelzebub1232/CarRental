from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, abort
import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, SECRET_KEY, DEBUG
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import csv
from io import StringIO
from flask import Response

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
    import datetime
    conn = get_db_connection()
    try:
        # Get vehicle details
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT base_price, type FROM vehicles WHERE id = %s", (vehicle_id,))
        vehicle = cursor.fetchone()
        cursor.close()
        if not vehicle:
            return None

        base_price = float(vehicle['base_price'])
        vehicle_type = vehicle['type']

        # Calculate duration in hours
        duration_hours = (end_datetime - start_datetime).total_seconds() / 3600
        calculated_price = base_price * duration_hours

        # Apply time-based peak modifiers
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pricing_rules WHERE rule_type = 'time_peak' AND is_active = TRUE")
        time_rules = cursor.fetchall()
        cursor.close()

        for rule in time_rules:
            peak_start = rule['peak_start_time']
            peak_end = rule['peak_end_time']
            booking_time = start_datetime.time()

            # Convert to time if needed
            if isinstance(peak_start, datetime.timedelta):
                peak_start = (datetime.datetime.min + peak_start).time()
            if isinstance(peak_end, datetime.timedelta):
                peak_end = (datetime.datetime.min + peak_end).time()

            # Handle time comparison properly
            if peak_start <= peak_end:
                # Same day peak hours (e.g., 9:00 to 17:00)
                if peak_start <= booking_time <= peak_end:
                    calculated_price *= (1 + float(rule['modifier_percentage']) / 100)
            else:
                # Overnight peak hours (e.g., 22:00 to 06:00)
                if booking_time >= peak_start or booking_time <= peak_end:
                    calculated_price *= (1 + float(rule['modifier_percentage']) / 100)

        # Apply demand-based modifiers for car type
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT modifier_percentage FROM pricing_rules WHERE rule_type = 'demand_car_type' AND vehicle_type = %s AND is_active = TRUE",
            (vehicle_type,)
        )
        demand_rule = cursor.fetchone()
        cursor.close()
        if demand_rule:
            calculated_price *= (1 + float(demand_rule['modifier_percentage']) / 100)

        return round(calculated_price, 2)

    finally:
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
        SELECT b.id, b.status AS booking_status, b.start_date, b.end_date, b.total_price, b.discount_applied, b.loyalty_token_used, b.booking_date, v.make, v.model, v.year, v.type, v.image_url
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
    
    cursor.execute("SELECT * FROM vehicles WHERE status = 'available' ORDER BY make, model")
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
        SELECT b.id, b.status AS booking_status, b.start_date, b.end_date, b.total_price, b.discount_applied, b.loyalty_token_used, b.booking_date, v.make, v.model, v.year, v.type
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

# Remove /customer/payment and /api/process_payment_and_booking routes and session['pending_booking'] logic

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
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        vehicle_id = data.get('vehicle_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Validate required fields
        if not vehicle_id:
            return jsonify({'error': 'vehicle_id is required'}), 400
        if not start_date:
            return jsonify({'error': 'start_date is required'}), 400
        if not end_date:
            return jsonify({'error': 'end_date is required'}), 400
        
        # Convert vehicle_id to int
        try:
            vehicle_id = int(vehicle_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'vehicle_id must be a valid integer'}), 400
        
        # Parse dates
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
        except ValueError as e:
            return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
        
        # Validate that end_date is after start_date
        if end_datetime <= start_datetime:
            return jsonify({'error': 'End date must be after start date'}), 400
        
        price = calculate_final_price(vehicle_id, start_datetime, end_datetime)
        
        if price is None:
            return jsonify({'error': 'Vehicle not found or price calculation failed'}), 400
        
        return jsonify({'price': price})
    except Exception as e:
        print(f"Error in calculate_price API: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/create_booking', methods=['POST'])
def api_create_booking():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    vehicle_id = data.get('vehicle_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    discount_code = data.get('discount_code', '')
    loyalty_token_id = data.get('loyalty_token_id')
    
    # Validate required fields
    if not vehicle_id or not start_date or not end_date:
        return jsonify({'success': False, 'error': 'Missing required booking information.'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Parse dates
        start_datetime = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
        if end_datetime <= start_datetime:
            return jsonify({'success': False, 'error': 'End date/time must be after start date/time.'}), 400
        # Check vehicle exists and is available
        cursor.execute("SELECT * FROM vehicles WHERE id = %s AND status = 'available'", (vehicle_id,))
        vehicle = cursor.fetchone()
        if not vehicle:
            return jsonify({'success': False, 'error': 'Selected vehicle is not available.'}), 400
        # Check for overlapping bookings
        cursor.execute("""
            SELECT * FROM bookings WHERE vehicle_id = %s AND status IN ('pending', 'approved')
            AND (
                (start_date <= %s AND end_date > %s) OR
                (start_date < %s AND end_date >= %s) OR
                (start_date >= %s AND end_date <= %s)
            )
        """, (vehicle_id, start_datetime, start_datetime, end_datetime, end_datetime, start_datetime, end_datetime))
        overlap = cursor.fetchone()
        if overlap:
            return jsonify({'success': False, 'error': 'This vehicle is already booked for the selected time range.'}), 400
        # Calculate base price
        total_price = calculate_final_price(vehicle_id, start_datetime, end_datetime)
        if total_price is None:
            return jsonify({'success': False, 'error': 'Could not calculate price for this booking.'}), 400
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
            else:
                return jsonify({'success': False, 'error': 'Invalid or expired discount code.'}), 400
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
            else:
                return jsonify({'success': False, 'error': 'Invalid or expired loyalty token.'}), 400
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
        import traceback
        print('Booking error:', traceback.format_exc())
        conn.rollback()
        return jsonify({'success': False, 'error': 'An unexpected error occurred while creating your booking. Please try again or contact support.'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/validate_discount', methods=['POST'])
def api_validate_discount():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    discount_code = data.get('discount_code', '').strip()
    vehicle_id = data.get('vehicle_id')
    vehicle_type = data.get('vehicle_type')
    
    if not discount_code:
        return jsonify({'error': 'Discount code is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if discount code exists and is valid
        cursor.execute("""
            SELECT * FROM discounts 
            WHERE code = %s AND is_active = TRUE 
            AND start_date <= CURDATE() AND end_date >= CURDATE()
            AND (usage_limit = 0 OR times_used < usage_limit)
        """, (discount_code,))
        discount = cursor.fetchone()
        
        if not discount:
            return jsonify({'error': 'Invalid or expired discount code'}), 400
        
        # Check if discount applies to this vehicle type
        if discount['vehicle_type'] and vehicle_type:
            if discount['vehicle_type'] not in vehicle_type:
                return jsonify({'error': f'Discount code only applies to {discount["vehicle_type"]} vehicles'}), 400
        
        # Check if discount applies to specific vehicle
        if discount['vehicle_id'] and vehicle_id:
            if discount['vehicle_id'] != vehicle_id:
                return jsonify({'error': 'Discount code does not apply to this vehicle'}), 400
        
        return jsonify({
            'valid': True,
            'discount_percentage': float(discount['discount_percentage']),
            'description': discount.get('description', ''),
            'code': discount['code']
        })
        
    except Exception as e:
        print(f"Error validating discount: {str(e)}")
        return jsonify({'error': 'Error validating discount code'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/loyalty_tokens', methods=['GET'])
def api_loyalty_tokens():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, token_value, expiry_date, description
            FROM loyalty_tokens
            WHERE user_id = %s AND is_redeemed = FALSE AND (expiry_date IS NULL OR expiry_date > NOW())
            ORDER BY issued_date DESC
        """, (session['user_id'],))
        tokens = cursor.fetchall()
        # Convert expiry_date to string for JSON
        for t in tokens:
            if t['expiry_date']:
                t['expiry_date'] = t['expiry_date'].strftime('%Y-%m-%d')
        return jsonify({'tokens': tokens})
    finally:
        cursor.close()
        conn.close()

@app.route('/api/loyalty_tokens', methods=['POST'])
def api_issue_loyalty_token():
    require_admin()
    data = request.get_json()
    email = data.get('email')
    token_value = data.get('value')
    expiry_date = data.get('expiry_date')
    description = data.get('description')
    if not email or not token_value:
        return jsonify({'success': False, 'error': 'Email and value are required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO loyalty_tokens (user_id, token_value, expiry_date, description)
            VALUES (%s, %s, %s, %s)
        """, (
            user['id'],
            token_value,
            expiry_date,
            description
        ))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
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

# --- Vehicle Management API (Admin Only) ---

def require_admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        abort(403)

@app.route('/api/vehicles', methods=['GET'])
def api_list_vehicles():
    require_admin()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicles ORDER BY make, model")
    vehicles = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'vehicles': vehicles})

@app.route('/api/vehicles', methods=['POST'])
def api_add_vehicle():
    require_admin()
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO vehicles (make, model, year, type, base_price, availability, status, pickup_location_lat, pickup_location_lng, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('make'),
            data.get('model'),
            data.get('year'),
            data.get('type'),
            data.get('base_price'),
            data.get('availability', True),
            data.get('status', 'available'),
            data.get('pickup_lat'),
            data.get('pickup_lng'),
            data.get('image_url')
        ))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vehicles/<int:vehicle_id>', methods=['GET'])
def api_get_vehicle(vehicle_id):
    require_admin()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicles WHERE id = %s", (vehicle_id,))
    vehicle = cursor.fetchone()
    cursor.close()
    conn.close()
    if not vehicle:
        return jsonify({'success': False, 'error': 'Vehicle not found'}), 404
    return jsonify(vehicle)

@app.route('/api/vehicles/<int:vehicle_id>', methods=['PUT'])
def api_update_vehicle(vehicle_id):
    require_admin()
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE vehicles SET make=%s, model=%s, year=%s, type=%s, base_price=%s, image_url=%s, pickup_location_lat=%s, pickup_location_lng=%s, status=%s
            WHERE id=%s
        """, (
            data.get('make'),
            data.get('model'),
            data.get('year'),
            data.get('type'),
            data.get('base_price'),
            data.get('image_url'),
            data.get('pickup_lat'),
            data.get('pickup_lng'),
            data.get('status', 'available'),
            vehicle_id
        ))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vehicles/<int:vehicle_id>', methods=['DELETE'])
def api_delete_vehicle(vehicle_id):
    require_admin()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM vehicles WHERE id = %s", (vehicle_id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vehicles/<int:vehicle_id>/availability', methods=['PUT'])
def api_toggle_vehicle_availability(vehicle_id):
    require_admin()
    data = request.get_json()
    availability = data.get('availability', True)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE vehicles SET availability = %s WHERE id = %s", (availability, vehicle_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/discounts', methods=['POST'])
def api_create_discount():
    require_admin()
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO discounts (code, discount_percentage, start_date, end_date, vehicle_id, vehicle_type, usage_limit, times_used, is_active, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s, %s)
        """, (
            data.get('code'),
            data.get('discount_percentage'),
            data.get('start_date'),
            data.get('end_date'),
            data.get('vehicle_id'),
            data.get('vehicle_type'),
            data.get('usage_limit', 0),
            data.get('is_active', True),
            data.get('description')
        ))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/bookings')
def admin_bookings():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    status = request.args.get('status')
    search = request.args.get('search')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = '''
        SELECT b.*, u.full_name, u.email, v.make, v.model
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN vehicles v ON b.vehicle_id = v.id
    '''
    filters = []
    params = []
    if status:
        filters.append('b.status = %s')
        params.append(status)
    if search:
        filters.append('(u.full_name LIKE %s OR v.make LIKE %s OR v.model LIKE %s OR b.id = %s)')
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%', search if search.isdigit() else -1])
    if filters:
        query += ' WHERE ' + ' AND '.join(filters)
    query += ' ORDER BY b.booking_date DESC'
    cursor.execute(query, tuple(params))
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/api/bookings/<int:booking_id>')
def api_booking_details(booking_id):
    require_admin()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT b.*, u.full_name, u.email, v.make, v.model, v.year, v.type, v.image_url
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN vehicles v ON b.vehicle_id = v.id
        WHERE b.id = %s
    ''', (booking_id,))
    booking = cursor.fetchone()
    cursor.close()
    conn.close()
    if not booking:
        return '<div class="modal-content"><h3>Booking not found</h3><button class="btn btn-outline modal-close">Close</button></div>'
    # Render details as HTML for modal
    return f'''
    <div class="modal-content">
        <h3>Booking Details</h3>
        <p><strong>ID:</strong> #{booking['id']}</p>
        <p><strong>Customer:</strong> {booking['full_name']} ({booking['email']})</p>
        <p><strong>Vehicle:</strong> {booking['make']} {booking['model']} ({booking['year']}, {booking['type']})</p>
        <p><strong>Dates:</strong> {booking['start_date']} to {booking['end_date']}</p>
        <p><strong>Total Price:</strong> ₹{booking['total_price']:.2f}</p>
        <p><strong>Status:</strong> {booking['status'].title()}</p>
        <p><strong>Discount Applied:</strong> ₹{booking['discount_applied']:.2f}</p>
        <p><strong>Loyalty Token Used:</strong> ₹{booking['loyalty_token_used']:.2f}</p>
        <button class="btn btn-outline modal-close">Close</button>
    </div>
    '''

@app.route('/api/bookings/<int:booking_id>/status', methods=['PUT'])
def api_update_booking_status_v2(booking_id):
    require_admin()
    data = request.get_json()
    status = data.get('status')
    if status not in ['pending', 'approved', 'rejected', 'completed', 'cancelled', 'paid']:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        # Only allow marking as completed if status is 'paid' and end_date has passed
        if status == 'completed':
            from datetime import datetime
            if booking['status'] != 'paid':
                return jsonify({'success': False, 'error': 'Booking must be paid before completion'}), 400
            if booking['end_date'] > datetime.now():
                return jsonify({'success': False, 'error': 'Cannot complete booking before rental period ends'}), 400
        cursor.execute("UPDATE bookings SET status = %s WHERE id = %s", (status, booking_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/customer/review/<int:booking_id>', methods=['GET', 'POST'])
def customer_review(booking_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Check booking ownership and status
    cursor.execute("SELECT * FROM bookings WHERE id = %s AND user_id = %s", (booking_id, user_id))
    booking = cursor.fetchone()
    if not booking or booking['status'] != 'completed':
        flash('You can only review completed bookings.')
        cursor.close()
        conn.close()
        return redirect(url_for('customer_dashboard'))
    # Check if already reviewed
    cursor.execute("SELECT * FROM reviews WHERE booking_id = %s AND user_id = %s", (booking_id, user_id))
    review = cursor.fetchone()
    if request.method == 'POST':
        if review:
            flash('You have already reviewed this booking.')
            cursor.close()
            conn.close()
            return redirect(url_for('customer_dashboard'))
        rating = int(request.form.get('rating', 0))
        comment = request.form.get('comment', '')
        if not (1 <= rating <= 5):
            flash('Rating must be between 1 and 5.')
            cursor.close()
            conn.close()
            return redirect(request.url)
        cursor.execute("""
            INSERT INTO reviews (booking_id, user_id, rating, comment)
            VALUES (%s, %s, %s, %s)
        """, (booking_id, user_id, rating, comment))
        conn.commit()
        flash('Thank you for your review!')
        cursor.close()
        conn.close()
        return redirect(url_for('customer_dashboard'))
    cursor.close()
    conn.close()
    return render_template('customer/review.html', booking=booking, review=review)

@app.route('/api/users', methods=['GET'])
def api_list_users():
    require_admin()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, email, full_name, role FROM users ORDER BY id")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'users': users})

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def api_edit_user(user_id):
    require_admin()
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users SET email=%s, full_name=%s, role=%s WHERE id=%s
        """, (
            data.get('email'),
            data.get('full_name'),
            data.get('role'),
            user_id
        ))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/users/<int:user_id>/reset_password', methods=['POST'])
def api_reset_user_password(user_id):
    require_admin()
    data = request.get_json()
    new_password = data.get('new_password')
    if not new_password:
        return jsonify({'success': False, 'error': 'New password required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new_password, user_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    require_admin()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/payments', methods=['GET'])
def api_list_payments():
    require_admin()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.booking_id, p.user_id, u.email, u.full_name, p.amount, p.payment_date, p.status, p.method, p.reference
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.payment_date DESC
    """)
    payments = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'payments': payments})

@app.route('/admin/payments')
def admin_payments():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/payments.html')

@app.route('/api/export/bookings')
def export_bookings():
    require_admin()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bookings ORDER BY booking_date DESC")
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    si = StringIO()
    writer = csv.DictWriter(si, fieldnames=bookings[0].keys() if bookings else [])
    writer.writeheader()
    writer.writerows(bookings)
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=bookings.csv"})

@app.route('/api/export/payments')
def export_payments():
    require_admin()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM payments ORDER BY payment_date DESC")
    payments = cursor.fetchall()
    cursor.close()
    conn.close()
    si = StringIO()
    writer = csv.DictWriter(si, fieldnames=payments[0].keys() if payments else [])
    writer.writeheader()
    writer.writerows(payments)
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=payments.csv"})

@app.route('/api/export/vehicles')
def export_vehicles():
    require_admin()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicles ORDER BY id")
    vehicles = cursor.fetchall()
    cursor.close()
    conn.close()
    si = StringIO()
    writer = csv.DictWriter(si, fieldnames=vehicles[0].keys() if vehicles else [])
    writer.writeheader()
    writer.writerows(vehicles)
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=vehicles.csv"})

@app.route('/api/vehicle_types', methods=['GET'])
def api_vehicle_types():
    require_admin()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT type FROM vehicles ORDER BY type")
    types = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify({'types': types})

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/users.html')

@app.route('/api/pay_for_booking', methods=['POST'])
def api_pay_for_booking():
    if 'user_id' not in session or session.get('role') != 'customer':
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    data = request.get_json()
    booking_id = data.get('booking_id')
    if not booking_id:
        return jsonify({'success': False, 'error': 'Missing booking ID'}), 400
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Check booking exists, is approved, and belongs to user
        cursor.execute("SELECT * FROM bookings WHERE id = %s AND user_id = %s", (booking_id, session['user_id']))
        booking = cursor.fetchone()
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        if booking['status'] != 'approved':
            return jsonify({'success': False, 'error': 'Booking is not approved or already paid'}), 400
        # Record payment (status 'success' is for the payment record, not the booking)
        cursor.execute("""
            INSERT INTO payments (booking_id, user_id, amount, status, method)
            VALUES (%s, %s, %s, %s, %s)
        """, (booking_id, session['user_id'], booking['total_price'], 'success', 'dummy'))
        # Update booking status to 'paid' (this is the key line)
        cursor.execute("UPDATE bookings SET status = %s WHERE id = %s", ('paid', booking_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=DEBUG)