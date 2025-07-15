from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, abort
import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, SECRET_KEY, DEBUG, LOYALTY_PERCENTAGE, LOYALTY_EXPIRY_DAYS, BOOKING_WINDOW_DAYS, MIN_BOOKING_DURATION_HOURS, MESSAGES

from datetime import datetime, timedelta
import json
import csv
from io import StringIO
from flask import Response
import re
import logging
from functools import wraps
from typing import Any, Dict, List, Optional, cast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['DEBUG'] = DEBUG
app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP in development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Custom error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html', error_code=403, error_message="Access forbidden"), 403

# Input validation functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 3:
        return False, "Password must be at least 3 characters long"
    return True, "Password is valid"

def validate_booking_data(vehicle_id, start_date, end_date):
    """Validate booking data"""
    errors = []
    
    # Convert vehicle_id to int if it's a string
    try:
        if vehicle_id:
            vehicle_id = int(vehicle_id)
        else:
            errors.append("Vehicle ID is required")
            return errors, None, None
    except (ValueError, TypeError):
        errors.append("Invalid vehicle ID")
        return errors, None, None
    
    if not start_date:
        errors.append("Start date is required")
        return errors, None, None
    
    if not end_date:
        errors.append("End date is required")
        return errors, None, None
    
    try:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
        
        if end_datetime <= start_datetime:
            errors.append("End date/time must be after start date/time")
        
        if start_datetime < datetime.now():
            errors.append("Start date cannot be in the past")
            
        # Check if booking is not more than 30 days in advance
        if start_datetime > datetime.now() + timedelta(days=30):
            errors.append("Bookings cannot be made more than 30 days in advance")
            
    except ValueError:
        errors.append("Invalid date format")
        return errors, None, None
    
    return errors, start_datetime, end_datetime

# Database connection with error handling
def get_db_connection():
    """Get database connection with proper error handling"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            autocommit=False
        )
        return conn
    except mysql.connector.Error as e:
        logger.error(f"Database connection error: {e}")
        raise Exception("Database connection failed. Please try again later.")

def safe_db_operation(operation_func):
    """Decorator for safe database operations"""
    @wraps(operation_func)
    def wrapper(*args, **kwargs):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            result = operation_func(cursor, *args, **kwargs)
            conn.commit()
            return result
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation error: {e}")
            raise Exception("Database operation failed. Please try again later.")
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return wrapper

# Duplicate booking prevention
def check_duplicate_booking(cursor, user_id, vehicle_id, start_datetime, end_datetime):
    """Check for duplicate bookings within a short time window"""
    # Check for recent bookings by the same user for the same vehicle
    cursor.execute("""
        SELECT id FROM bookings 
        WHERE user_id = %s AND vehicle_id = %s 
        AND booking_date > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
        AND status IN ('pending', 'approved')
    """, (user_id, vehicle_id))
    
    if cursor.fetchone():
        return True, "You have already made a booking for this vehicle recently. Please wait a few minutes before trying again."
    
    return False, None

def calculate_final_price(vehicle_id, start_datetime, end_datetime, return_breakdown=False):
    """Calculate final price robustly for any rental duration"""
    import datetime
    conn = get_db_connection()
    try:
        # Get vehicle details
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT base_price, type FROM vehicles WHERE id = %s", (vehicle_id,))
        vehicle = cursor.fetchone()
        vehicle = cast(Optional[Dict[str, Any]], vehicle)
        cursor.close()
        if not vehicle:
            return None

        base_price = float(vehicle['base_price'])
        vehicle_type = vehicle['type']

        # Calculate duration in hours, round up to next full hour
        duration_seconds = (end_datetime - start_datetime).total_seconds()
        if duration_seconds <= 0:
            return 0
        duration_hours = int(-(-duration_seconds // 3600))  # Ceiling division

        # Get peak pricing rules
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pricing_rules WHERE rule_type = 'time_peak' AND is_active = TRUE")
        time_rules = cursor.fetchall()
        time_rules = cast(List[Dict[str, Any]], time_rules)
        cursor.close()

        # Get demand modifier for car type
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT modifier_percentage FROM pricing_rules WHERE rule_type = 'demand_car_type' AND vehicle_type = %s AND is_active = TRUE",
            (vehicle_type,)
        )
        demand_rule = cursor.fetchone()
        demand_rule = cast(Optional[Dict[str, Any]], demand_rule)
        cursor.close()
        demand_multiplier = 1.0
        demand_percentage = 0.0
        if demand_rule:
            demand_percentage = float(demand_rule['modifier_percentage'])
            demand_multiplier += demand_percentage / 100

        # Calculate price hour by hour
        total_price = 0.0
        base_total = base_price * duration_hours
        peak_adjustments = 0.0
        peak_hours = 0
        
        for i in range(duration_hours):
            hour_time = (start_datetime + timedelta(hours=i)).time()
            hour_multiplier = 1.0
            hour_peak_adjustment = 0.0
            
            for rule in time_rules:
                peak_start = rule['peak_start_time']
                peak_end = rule['peak_end_time']
                # Convert to time if needed
                if isinstance(peak_start, datetime.timedelta):
                    peak_start = (datetime.datetime.min + peak_start).time()
                if isinstance(peak_end, datetime.timedelta):
                    peak_end = (datetime.datetime.min + peak_end).time()
                # Handle time comparison
                if peak_start <= peak_end:
                    if peak_start <= hour_time <= peak_end:
                        hour_multiplier += float(rule['modifier_percentage']) / 100
                        hour_peak_adjustment += base_price * (float(rule['modifier_percentage']) / 100)
                else:
                    if hour_time >= peak_start or hour_time <= peak_end:
                        hour_multiplier += float(rule['modifier_percentage']) / 100
                        hour_peak_adjustment += base_price * (float(rule['modifier_percentage']) / 100)
            
            if hour_peak_adjustment > 0:
                peak_hours += 1
                peak_adjustments += hour_peak_adjustment
            
            total_price += base_price * hour_multiplier * demand_multiplier

        # Minimum charge for 1 hour
        if total_price < base_price:
            total_price = base_price
        # Cap to a reasonable max (e.g., 30 days)
        max_hours = 30 * 24
        if duration_hours > max_hours:
            total_price = base_price * max_hours * demand_multiplier
            
        final_price = round(total_price, 2)
        
        if return_breakdown:
            return {
                'total_price': final_price,
                'base_price_per_hour': base_price,
                'duration_hours': duration_hours,
                'base_total': round(base_total, 2),
                'peak_adjustments': round(peak_adjustments, 2),
                'peak_hours': peak_hours,
                'demand_multiplier': demand_multiplier,
                'demand_percentage': demand_percentage,
                'vehicle_type': vehicle_type,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime
            }
        else:
            return final_price
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
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Input validation
        if not email or not password:
            flash('Please provide both email and password')
            return render_template('login.html')
        
        if not validate_email(email):
            flash('Please enter a valid email address')
            return render_template('login.html')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            user = cast(Optional[Dict[str, Any]], user)
            
            if user and user['password'] == password:
                session['user_id'] = user['id']
                session['role'] = user['role']
                session['full_name'] = user['full_name']
                
                logger.info(f"User {user['email']} logged in successfully. Session set: user_id={session['user_id']}, role={session['role']}")
                
                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('customer_dashboard'))
            else:
                logger.warning(f"Failed login attempt for email: {email}")
                flash('Invalid email or password')
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('An error occurred during login. Please try again.')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        
        # Input validation
        if not email or not password or not full_name:
            flash('Please fill in all required fields')
            return render_template('login.html')
        
        if not validate_email(email):
            flash('Please enter a valid email address')
            return render_template('login.html')
        
        is_valid, password_message = validate_password(password)
        if not is_valid:
            flash(password_message)
            return render_template('login.html')
        
        if len(full_name) < 2 or len(full_name) > 100:
            flash('Full name must be between 2 and 100 characters')
            return render_template('login.html')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO users (email, password, full_name, role) VALUES (%s, %s, %s, 'customer')",
                (email, password, full_name)
            )
            conn.commit()
            
            logger.info(f"New user registered: {email}")
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
            
        except mysql.connector.IntegrityError:
            flash('Email already exists')
        except Exception as e:
            logger.error(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.')
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
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get recent bookings
        cursor.execute("""
            SELECT b.id, b.status AS booking_status, b.start_date, b.end_date, b.total_price, b.discount_applied, b.loyalty_token_used, b.booking_date, v.make, v.model, v.year, v.type, v.image_url,
                   CASE WHEN r.id IS NOT NULL THEN 1 ELSE 0 END as has_review
            FROM bookings b
            JOIN vehicles v ON b.vehicle_id = v.id
            LEFT JOIN reviews r ON b.id = r.booking_id AND r.user_id = %s
            WHERE b.user_id = %s
            ORDER BY b.booking_date DESC
            LIMIT 5
        """, (session['user_id'], session['user_id']))
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
                             loyalty_tokens=loyalty_tokens,
                             messages=MESSAGES)
                             
    except Exception as e:
        logger.error(f"Customer dashboard error: {e}")
        flash('An error occurred while loading your dashboard. Please try again.')
        return render_template('customer/dashboard.html', 
                             recent_bookings=[], 
                             loyalty_tokens=[],
                             messages=MESSAGES)

@app.route('/customer/booking')
def customer_booking():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    
    # Debug logging
    logger.info(f"Customer booking page accessed by user_id: {session.get('user_id')}, role: {session.get('role')}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM vehicles WHERE status = 'available' ORDER BY make, model")
        vehicles = cursor.fetchall()
        
        # Also check if user has any loyalty tokens for debugging
        cursor.execute("""
            SELECT COUNT(*) as token_count 
            FROM loyalty_tokens 
            WHERE user_id = %s AND is_redeemed = FALSE AND (expiry_date IS NULL OR expiry_date > NOW())
        """, (session['user_id'],))
        token_count_row = cursor.fetchone()
        token_count_row = cast(Optional[Dict[str, Any]], token_count_row)
        token_count = token_count_row['token_count'] if token_count_row else 0
        logger.info(f"User {session['user_id']} has {token_count} available loyalty tokens")
        
        cursor.close()
        conn.close()
        
        return render_template('customer/booking.html', vehicles=vehicles, messages=MESSAGES)
        
    except Exception as e:
        logger.error(f"Customer booking page error: {e}")
        flash('An error occurred while loading available vehicles. Please try again.')
        return render_template('customer/booking.html', vehicles=[], messages=MESSAGES)

@app.route('/customer/profile')
def customer_profile():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get user details
        cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        # Get all bookings
        cursor.execute("""
            SELECT b.id, b.status AS booking_status, b.start_date, b.end_date, b.total_price, b.discount_applied, b.loyalty_token_used, b.booking_date, v.make, v.model, v.year, v.type,
                   CASE WHEN r.id IS NOT NULL THEN 1 ELSE 0 END as has_review
            FROM bookings b
            JOIN vehicles v ON b.vehicle_id = v.id
            LEFT JOIN reviews r ON b.id = r.booking_id AND r.user_id = %s
            WHERE b.user_id = %s
            ORDER BY b.booking_date DESC
        """, (session['user_id'], session['user_id']))
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
                             loyalty_tokens=loyalty_tokens,
                             messages=MESSAGES)
                             
    except Exception as e:
        logger.error(f"Customer profile error: {e}")
        flash('An error occurred while loading your profile. Please try again.')
        return render_template('customer/profile.html', 
                             user=None, 
                             bookings=[], 
                             loyalty_tokens=[],
                             messages=MESSAGES)

@app.route('/customer/bookings')
def customer_bookings():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT b.id, b.status AS booking_status, b.start_date, b.end_date, b.total_price, b.discount_applied, b.loyalty_token_used, b.booking_date, v.make, v.model, v.year, v.type,
                   CASE WHEN r.id IS NOT NULL THEN 1 ELSE 0 END as has_review
            FROM bookings b
            JOIN vehicles v ON b.vehicle_id = v.id
            LEFT JOIN reviews r ON b.id = r.booking_id AND r.user_id = %s
            WHERE b.user_id = %s
            ORDER BY b.booking_date DESC
        """, (session['user_id'], session['user_id']))
        bookings = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('customer/bookings.html', bookings=bookings, messages=MESSAGES)
        
    except Exception as e:
        logger.error(f"Customer bookings error: {e}")
        flash('An error occurred while loading your bookings. Please try again.')
        return render_template('customer/bookings.html', bookings=[], messages=MESSAGES)

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
    total_vehicles_row = cursor.fetchone()
    total_vehicles_row = cast(Optional[Dict[str, Any]], total_vehicles_row)
    total_vehicles = total_vehicles_row['total'] if total_vehicles_row else 0
    
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'customer'")
    total_customers_row = cursor.fetchone()
    total_customers_row = cast(Optional[Dict[str, Any]], total_customers_row)
    total_customers = total_customers_row['total'] if total_customers_row else 0
    
    cursor.execute("SELECT COUNT(*) as total FROM bookings WHERE status = 'pending'")
    pending_bookings_row = cursor.fetchone()
    pending_bookings_row = cast(Optional[Dict[str, Any]], pending_bookings_row)
    pending_bookings = pending_bookings_row['total'] if pending_bookings_row else 0
    
    cursor.execute("SELECT SUM(total_price) as total FROM bookings WHERE status = 'completed'")
    total_revenue_row = cursor.fetchone()
    total_revenue_row = cast(Optional[Dict[str, Any]], total_revenue_row)
    total_revenue = (total_revenue_row['total'] if total_revenue_row else 0) or 0
    
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
        
        price_breakdown = calculate_final_price(vehicle_id, start_datetime, end_datetime, return_breakdown=True)
        
        if price_breakdown is None:
            return jsonify({'error': 'Vehicle not found or price calculation failed'}), 400
        
        return jsonify(price_breakdown)
    except Exception as e:
        print(f"Error in calculate_price API: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/create_booking', methods=['POST'])
def api_create_booking():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid request data'}), 400
        
        vehicle_id = data.get('vehicle_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        discount_code = data.get('discount_code', '').strip()
        loyalty_token_id = data.get('loyalty_token_id')
        
        # Debug logging
        logger.info(f"Booking request data: vehicle_id={vehicle_id}, start_date={start_date}, end_date={end_date}")
        
        # Comprehensive input validation
        validation_errors, start_datetime, end_datetime = validate_booking_data(vehicle_id, start_date, end_date)
        if validation_errors:
            return jsonify({'success': False, 'error': validation_errors[0]}), 400
        
        # Convert vehicle_id to int for database operations
        vehicle_id = int(vehicle_id)
        
        # Validate discount code format if provided
        if discount_code and len(discount_code) > 50:
            return jsonify({'success': False, 'error': 'Discount code is too long'}), 400
        
        # Validate loyalty token ID if provided
        if loyalty_token_id and not isinstance(loyalty_token_id, int):
            return jsonify({'success': False, 'error': 'Invalid loyalty token ID'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Check for duplicate booking
            is_duplicate, duplicate_message = check_duplicate_booking(cursor, session['user_id'], vehicle_id, start_datetime, end_datetime)
            if is_duplicate:
                return jsonify({'success': False, 'error': duplicate_message}), 400
            
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
            if not (isinstance(total_price, float) or total_price is None):
                logger.error(f"calculate_final_price returned non-float: {type(total_price)} value={total_price}")
                return jsonify({'success': False, 'error': 'Internal error: price calculation returned invalid type.'}), 500
            if total_price is None:
                return jsonify({'success': False, 'error': 'Could not calculate price for this booking.'}), 400
            discount_applied = 0.0
            loyalty_token_used = 0.0
            if total_price is not None:
                total_price = float(total_price)
            
            # Apply discount code if provided
            if discount_code:
                cursor.execute("""
                    SELECT * FROM discounts 
                    WHERE code = %s AND is_active = TRUE 
                    AND start_date <= CURDATE() AND end_date >= CURDATE()
                    AND (usage_limit = 0 OR times_used < usage_limit)
                """, (discount_code,))
                discount_row = cursor.fetchone()
                discount = cast(Optional[Dict[str, Any]], discount_row)
                if discount:
                    percent = float(discount['discount_percentage'])
                    discount_applied = float(total_price) * (percent / 100)
                    total_price = float(total_price) - discount_applied
                    discount_applied = float(discount_applied)
                    total_price = float(total_price)
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
                    FOR UPDATE
                """, (loyalty_token_id, session['user_id']))
                token_row = cursor.fetchone()
                token = cast(Optional[Dict[str, Any]], token_row)
                if token:
                    token_value = float(token['token_value'])
                    total_price = float(total_price)
                    min_token = min(token_value, total_price)
                    loyalty_token_used = float(min_token)
                    total_price = float(total_price - loyalty_token_used)
                    loyalty_token_used = float(loyalty_token_used)
                    total_price = float(total_price)
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
            
            conn.commit()
            
            logger.info(f"Booking created successfully: ID {booking_id} by user {session['user_id']}")
            
            return jsonify({
                'success': True, 
                'booking_id': booking_id,
                'total_price': total_price,
                'loyalty_earned': 0  # No loyalty earned until booking is completed
            })
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Booking creation error: {e}")
            return jsonify({'success': False, 'error': f'An unexpected error occurred while creating your booking: {str(e)}'}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"API create booking error: {e}")
        return jsonify({'success': False, 'error': 'Invalid request format'}), 400

@app.route('/api/validate_discount', methods=['POST'])
def api_validate_discount():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    discount_code = data.get('discount_code', '').strip()
    vehicle_id = data.get('vehicle_id')
    vehicle_type = data.get('vehicle_type')
    
    # Debug logging
    logger.info(f"Discount validation request: code={discount_code}, vehicle_id={vehicle_id}, vehicle_type={vehicle_type}")
    
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
        discount = cast(Optional[Dict[str, Any]], discount)
        if not discount:
            logger.warning(f"Discount code not found or invalid: {discount_code}")
            return jsonify({'error': 'Invalid or expired discount code'}), 400
        
        # Debug logging for discount found
        logger.info(f"Discount found: {discount}")
        
        # Check if discount applies to this vehicle type
        vehicle_type_db = discount.get('vehicle_type') if discount else None
        if vehicle_type_db and vehicle_type:
            logger.info(f"Checking vehicle type: discount_type={vehicle_type_db}, vehicle_type={vehicle_type}")
            if vehicle_type_db != vehicle_type:
                logger.warning(f"Vehicle type mismatch: {vehicle_type_db} != {vehicle_type}")
                return jsonify({'error': f'Discount code only applies to {vehicle_type_db} vehicles'}), 400
        
        # Check if discount applies to specific vehicle
        if discount['vehicle_id'] and vehicle_id:
            logger.info(f"Checking vehicle ID: discount_vehicle_id={discount['vehicle_id']}, vehicle_id={vehicle_id}")
            try:
                vehicle_id_int = int(vehicle_id)
                if discount['vehicle_id'] != vehicle_id_int:
                    logger.warning(f"Vehicle ID mismatch: {discount['vehicle_id']} != {vehicle_id_int}")
                    return jsonify({'error': 'Discount code does not apply to this vehicle'}), 400
            except (ValueError, TypeError):
                logger.error(f"Invalid vehicle ID format: {vehicle_id}")
                return jsonify({'error': 'Invalid vehicle ID'}), 400
        
        logger.info(f"Discount validation successful: {discount_code} - {discount['discount_percentage']}%")
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
    logger.info(f"Loyalty tokens API called by user_id: {session.get('user_id')}, role: {session.get('role')}")
    
    if 'user_id' not in session:
        logger.warning("Loyalty tokens API: User not authenticated")
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
        tokens = cast(List[Dict[str, Any]], tokens)
        logger.info(f"Found {len(tokens)} loyalty tokens for user {session['user_id']}")
        
        # Convert expiry_date to string for JSON
        for t in tokens:
            if t.get('expiry_date'):
                t['expiry_date'] = t['expiry_date'].strftime('%Y-%m-%d')
        
        return jsonify({'tokens': tokens})
    except Exception as e:
        logger.error(f"Error in loyalty tokens API: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/notifications', methods=['GET'])
def api_notifications():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, message, type, related_booking_id, is_read, created_at
            FROM customer_notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 10
        """, (session['user_id'],))
        notifications = cursor.fetchall()
        notifications = cast(List[Dict[str, Any]], notifications)
        # Convert datetime to string for JSON
        for n in notifications:
            if n.get('created_at'):
                n['created_at'] = n['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'notifications': notifications})
    finally:
        cursor.close()
        conn.close()

@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
def api_mark_notification_read(notification_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE customer_notifications 
            SET is_read = TRUE 
            WHERE id = %s AND user_id = %s
        """, (notification_id, session['user_id']))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
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
        user = cast(Optional[Dict[str, Any]], user)
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
    vehicles = cast(List[Dict[str, Any]], vehicles)
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
    vehicle = cast(Optional[Dict[str, Any]], vehicle)
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
    # Allow admin or the booking's owner (customer) to fetch booking details
    user_id = session.get('user_id')
    user_role = session.get('role')
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
    booking = cast(Optional[Dict[str, Any]], booking)
    cursor.close()
    conn.close()
    if not booking:
        if request.accept_mimetypes['application/json']:
            return jsonify({'error': 'Booking not found'}), 404
        return '<div><h3>Booking not found</h3><button class="btn btn-outline modal-close modal-close-x" aria-label="Close">&times;</button></div>'
    # Permission check: admin can view any, customer can only view their own
    if not (user_role == 'admin' or (user_role == 'customer' and booking['user_id'] == user_id)):
        if request.accept_mimetypes['application/json']:
            return jsonify({'error': 'Forbidden'}), 403
        return '<div><h3>Forbidden</h3><button class="btn btn-outline modal-close modal-close-x" aria-label="Close">&times;</button></div>'
    # If JSON requested, return JSON
    if request.accept_mimetypes['application/json']:
        return jsonify(booking)
    # Render details as HTML for modal (structured, modern, grouped)
    return f'''
    <div style="position: relative; min-width: 320px; max-width: 480px;">
        <button class="modal-close modal-close-x" aria-label="Close" style="position: absolute; top: 1rem; right: 1rem; background: none; border: none; font-size: 2rem; line-height: 1; cursor: pointer; color: #888;">&times;</button>
        <h2 style="margin-top:0; margin-bottom: 1.5rem; font-size: 1.5rem; font-weight: 800; letter-spacing: -1px;">Booking Details</h2>
        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                {'<img src="' + booking['image_url'] + '" alt="Vehicle" style="width: 72px; height: 48px; object-fit: cover; border-radius: 0.75rem; border: 1px solid #eee;">' if booking['image_url'] else ''}
                <div>
                    <div style="font-weight: 700; font-size: 1.1rem; color: #222;">{booking['make']} {booking['model']}</div>
                    <div style="color: #666; font-size: 0.95rem;">{booking['year']} {booking['type']}</div>
                </div>
            </div>
            <dl style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem 1.5rem; font-size: 1rem;">
                <dt style="color: #888;">Booking ID</dt><dd style="font-weight: 600; color: #2563eb;">#{booking['id']}</dd>
                <dt style="color: #888;">Customer</dt><dd style="font-weight: 600;">{booking['full_name']}<br><span style='color:#888;font-size:0.95em'>{booking['email']}</span></dd>
                <dt style="color: #888;">Dates</dt><dd>{booking['start_date']}<br>to {booking['end_date']}</dd>
                <dt style="color: #888;">Status</dt><dd style="font-weight: 600; text-transform: uppercase;">{booking['status'].title()}</dd>
                <dt style="color: #888;">Total Price</dt><dd style="font-weight: 700; color: #22c55e;">₹{booking['total_price']:.2f}</dd>
                <dt style="color: #888;">Discount</dt><dd>₹{booking['discount_applied']:.2f}</dd>
                <dt style="color: #888;">Loyalty Used</dt><dd>₹{booking['loyalty_token_used']:.2f}</dd>
            </dl>
        </div>
    </div>
    '''

@app.route('/api/bookings/<int:booking_id>/status', methods=['PUT'])
def api_update_booking_status_v2(booking_id):
    require_admin()
    data = request.get_json()
    status = data.get('status')
    print(f"[DEBUG] Incoming status update for booking {booking_id}: {data}")
    if status not in ['pending', 'approved', 'rejected', 'completed', 'cancelled', 'paid']:
        print(f"[DEBUG] Invalid status value: {status}")
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()
        booking = cast(Optional[Dict[str, Any]], booking)
        print(f"[DEBUG] Booking lookup result: {booking}")
        if not booking:
            print(f"[DEBUG] Booking not found for ID: {booking_id}")
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Check if this is a status change to 'completed'
        if status == 'completed' and booking['status'] != 'completed':
            # Issue loyalty token when booking is completed (5% of booking value)
            loyalty_value = float(booking['total_price']) * 0.05
            expiry_date = datetime.now() + timedelta(days=365)
            cursor.execute("""
                INSERT INTO loyalty_tokens (user_id, token_value, expiry_date, description)
                VALUES (%s, %s, %s, %s)
            """, (booking['user_id'], loyalty_value, expiry_date, f'Earned from completed booking #{booking_id}'))
            
            logger.info(f"Loyalty token issued for completed booking {booking_id}: {loyalty_value}")
            
            # Store a notification for the customer about the loyalty reward
            cursor.execute("""
                INSERT INTO customer_notifications (user_id, message, type, related_booking_id)
                VALUES (%s, %s, %s, %s)
            """, (booking['user_id'], f'Congratulations! You earned ₹{loyalty_value:.2f} in loyalty rewards for your completed booking #{booking_id}.', 'loyalty_reward', booking_id))
        
        print(f"[DEBUG] Updating booking {booking_id} to status: {status}")
        cursor.execute("UPDATE bookings SET status = %s WHERE id = %s", (status, booking_id))
        conn.commit()
        print(f"[DEBUG] Booking {booking_id} status updated successfully.")
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        print(f"[DEBUG] Exception during status update: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Remove all review system logic: routes, queries, and context variables related to reviews

@app.route('/customer/review/<int:booking_id>', methods=['GET', 'POST'])
def customer_review(booking_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get booking and check eligibility
    cursor.execute("""
        SELECT b.*, v.make, v.model, v.year, v.type
        FROM bookings b
        JOIN vehicles v ON b.vehicle_id = v.id
        WHERE b.id = %s AND b.user_id = %s
    """, (booking_id, user_id))
    booking = cursor.fetchone()
    booking = cast(Optional[Dict[str, Any]], booking)
    if not booking:
        flash('Booking not found.', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('customer_bookings'))
    if (booking.get('status') or booking.get('booking_status')) != 'completed':
        flash('You can only review completed bookings.', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('customer_bookings'))
    # Check if already reviewed
    cursor.execute("SELECT id FROM reviews WHERE booking_id = %s AND user_id = %s", (booking_id, user_id))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return render_template('customer/review_thankyou.html', booking=booking)

    if request.method == 'POST':
        rating = int(request.form.get('rating', 0))
        comment = request.form.get('comment', '').strip()
        recommend = request.form.get('recommend', '')
        # Validation
        if not (1 <= rating <= 5):
            flash('Rating must be between 1 and 5.', 'error')
            cursor.close()
            conn.close()
            return redirect(request.url)
        
        if len(comment) < 10:
            flash('Please provide a detailed review (at least 10 characters).', 'error')
            cursor.close()
            conn.close()
            return redirect(request.url)
        
        if not recommend:
            flash('Please indicate if you would recommend us.', 'error')
            cursor.close()
            conn.close()
            return redirect(request.url)
        
        # Get category ratings from form
        condition_rating = request.form.get('condition_rating')
        service_rating = request.form.get('service_rating')
        value_rating = request.form.get('value_rating')

        # Validate category ratings
        try:
            condition_rating = int(condition_rating) if condition_rating is not None else 0
            service_rating = int(service_rating) if service_rating is not None else 0
            value_rating = int(value_rating) if value_rating is not None else 0
        except (TypeError, ValueError):
            flash('Please rate all specific aspects (condition, service, value).', 'error')
            cursor.close()
            conn.close()
            return redirect(request.url)
        if not (1 <= condition_rating <= 5 and 1 <= service_rating <= 5 and 1 <= value_rating <= 5):
            flash('All aspect ratings must be between 1 and 5.', 'error')
            cursor.close()
            conn.close()
            return redirect(request.url)
        
        # Insert review with additional data
        cursor.execute("""
            INSERT INTO reviews (booking_id, user_id, rating, comment, recommend, condition_rating, service_rating, value_rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (booking_id, user_id, rating, comment, recommend, condition_rating, service_rating, value_rating))
        
        conn.commit()
        cursor.close()
        conn.close()
        flash('Your review has been submitted. Thank you!', 'success')
        return redirect(url_for('customer_reviews'))

    cursor.close()
    conn.close()
    return render_template('customer/review_form.html', booking=booking, messages=MESSAGES)

@app.route('/customer/review/edit/<int:review_id>', methods=['GET', 'POST'])
def customer_review_edit(review_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT r.*, b.id as booking_id, v.make, v.model, v.year
        FROM reviews r
        JOIN bookings b ON r.booking_id = b.id
        JOIN vehicles v ON b.vehicle_id = v.id
        WHERE r.id = %s AND r.user_id = %s
    ''', (review_id, user_id))
    review = cursor.fetchone()
    review = cast(Optional[Dict[str, Any]], review)
    if not review:
        cursor.close()
        conn.close()
        flash('Review not found or not authorized.', 'error')
        return redirect(url_for('customer_reviews'))
    if request.method == 'POST':
        rating = int(request.form.get('rating', 0))
        comment = request.form.get('comment', '').strip()
        recommend = request.form.get('recommend', '')
        if not (1 <= rating <= 5):
            flash('Rating must be between 1 and 5.', 'error')
            return render_template('customer/review_edit_form.html', review=review)
        if len(comment) < 10:
            flash('Please provide a detailed review (at least 10 characters).', 'error')
            return render_template('customer/review_edit_form.html', review=review)
        if recommend not in ['yes', 'maybe', 'no']:
            flash('Please indicate if you would recommend us.', 'error')
            return render_template('customer/review_edit_form.html', review=review)
        cursor.execute('''
            UPDATE reviews SET rating=%s, comment=%s, recommend=%s, review_date=NOW()
            WHERE id=%s AND user_id=%s
        ''', (rating, comment, recommend, review_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Review updated successfully.', 'success')
        return redirect(url_for('customer_reviews'))
    cursor.close()
    conn.close()
    return render_template('customer/review_edit_form.html', review=review)

@app.route('/customer/review/delete/<int:review_id>', methods=['POST'])
def customer_review_delete(review_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM reviews WHERE id = %s AND user_id = %s', (review_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Review deleted successfully.', 'success')
    return redirect(url_for('customer_reviews'))

@app.route('/customer/reviews')
def customer_reviews():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT r.*, b.id as booking_id, v.make, v.model, v.year
        FROM reviews r
        JOIN bookings b ON r.booking_id = b.id
        JOIN vehicles v ON b.vehicle_id = v.id
        WHERE r.user_id = %s
        ORDER BY r.review_date DESC
    ''', (user_id,))
    reviews = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('customer/reviews_list.html', reviews=reviews)

@app.route('/api/export/bookings')
def export_bookings():
    require_admin()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bookings ORDER BY booking_date DESC")
    bookings = cursor.fetchall()
    bookings = cast(List[Dict[str, Any]], bookings)
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
    payments = cast(List[Dict[str, Any]], payments)
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
    vehicles = cast(List[Dict[str, Any]], vehicles)
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

@app.route('/api/users')
def api_users():
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, email, full_name, role FROM users ORDER BY id")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'users': users})

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
    data = request.get_json()
    email = data.get('email')
    full_name = data.get('full_name')
    role = data.get('role')
    if not email or not full_name or not role:
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET email=%s, full_name=%s, role=%s WHERE id=%s", (email, full_name, role, user_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/users/<int:user_id>/reset_password', methods=['POST'])
def api_reset_user_password(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
    data = request.get_json()
    new_password = data.get('new_password')
    if not new_password:
        return jsonify({'success': False, 'error': 'Missing new password'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new_password, user_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

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
        booking = cast(Optional[Dict[str, Any]], booking)
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

# --- Admin Reviews Management ---
@app.route('/admin/reviews')
def admin_reviews():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Fetch all reviews with customer and vehicle info
    cursor.execute('''
        SELECT r.*, b.id as booking_id, u.full_name as customer_name, u.email as customer_email, v.make, v.model, v.type as vehicle_type
        FROM reviews r
        JOIN bookings b ON r.booking_id = b.id
        JOIN users u ON r.user_id = u.id
        JOIN vehicles v ON b.vehicle_id = v.id
        ORDER BY r.review_date DESC
    ''')
    reviews = cursor.fetchall()
    reviews = cast(List[Dict[str, Any]], reviews)
    # Stats
    total_reviews = len(reviews)
    average_rating = round(sum(r['rating'] for r in reviews) / total_reviews, 1) if total_reviews else 0
    recommend_count = sum(1 for r in reviews if r['recommend'] == 'yes')
    recommend_percentage = round((recommend_count / total_reviews) * 100, 1) if total_reviews else 0
    unique_vehicles = len(set((r['make'], r['model'], r['vehicle_type']) for r in reviews))
    # Rating distribution
    rating_counts = {i: 0 for i in range(1, 6)}
    for r in reviews:
        rating_counts[r['rating']] += 1
    rating_distribution = {i: round((rating_counts[i] / total_reviews) * 100, 1) if total_reviews else 0 for i in range(1, 6)}
    # Vehicle types for filter
    cursor.execute('SELECT DISTINCT type FROM vehicles ORDER BY type')
    vehicle_types = cursor.fetchall()
    vehicle_types = cast(List[Dict[str, Any]], vehicle_types)
    vehicle_types = [row['type'] for row in vehicle_types]
    cursor.close()
    conn.close()
    return render_template('admin/reviews.html',
        reviews=reviews,
        total_reviews=total_reviews,
        average_rating=average_rating,
        recommend_percentage=recommend_percentage,
        unique_vehicles=unique_vehicles,
        rating_counts=rating_counts,
        rating_distribution=rating_distribution,
        vehicle_types=vehicle_types
    )

# --- API: Delete Review (Admin Only) ---
@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
def api_delete_review(review_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM reviews WHERE id = %s', (review_id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# --- API: Export Reviews as CSV (Admin Only) ---
@app.route('/api/export/reviews')
def export_reviews():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT r.id, r.rating, r.comment, r.recommend, r.review_date, b.id as booking_id, u.full_name as customer_name, u.email as customer_email, v.make, v.model, v.type as vehicle_type
        FROM reviews r
        JOIN bookings b ON r.booking_id = b.id
        JOIN users u ON r.user_id = u.id
        JOIN vehicles v ON b.vehicle_id = v.id
        ORDER BY r.review_date DESC
    ''')
    reviews = cursor.fetchall()
    reviews = cast(List[Dict[str, Any]], reviews)
    cursor.close()
    conn.close()
    si = StringIO()
    if reviews:
        writer = csv.DictWriter(si, fieldnames=reviews[0].keys())
        writer.writeheader()
        writer.writerows(reviews)
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=reviews.csv"})

@app.route('/admin/payments')
def admin_payments():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT p.*, u.full_name as customer_name, u.email as customer_email, b.id as booking_id, v.make, v.model
        FROM payments p
        JOIN users u ON p.user_id = u.id
        JOIN bookings b ON p.booking_id = b.id
        JOIN vehicles v ON b.vehicle_id = v.id
        ORDER BY p.payment_date DESC
    ''')
    payments = cursor.fetchall()
    payments = cast(List[Dict[str, Any]], payments)
    cursor.close()
    conn.close()
    si = StringIO()
    writer = csv.DictWriter(si, fieldnames=payments[0].keys() if payments else [])
    writer.writeheader()
    writer.writerows(payments)
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=payments.csv"})

if __name__ == '__main__':
    app.run(debug=DEBUG)