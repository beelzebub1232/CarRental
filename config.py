# config.py
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "car_rental_db"

# Flask configuration
SECRET_KEY = "your_secret_key_here_change_in_production"
DEBUG = True

# Business rules
LOYALTY_PERCENTAGE = 0.05  # 5%
LOYALTY_EXPIRY_DAYS = 365
BOOKING_WINDOW_DAYS = 30
MIN_BOOKING_DURATION_HOURS = 1

# User-facing messages (can be localized later)
MESSAGES = {
    'empty_bookings': 'No bookings yet',
    'empty_loyalty': 'No loyalty tokens yet',
    'empty_vehicles': 'No vehicles available',
    'start_journey': 'Ready to start your journey?',
    'book_now': 'Book Your First Vehicle',
    'invalid_discount': 'Invalid or expired discount code.',
    'booking_success': 'Booking created successfully!',
    'booking_duplicate': 'You have already made a booking for this vehicle recently. Please wait a few minutes before trying again.',
    'booking_overlap': 'This vehicle is already booked for the selected time range.',
    'booking_window': f'Bookings cannot be made more than {BOOKING_WINDOW_DAYS} days in advance',
    'min_booking_duration': f'Minimum booking duration is {MIN_BOOKING_DURATION_HOURS} hour',
    'password_requirements': 'Password must be at least 3 characters long.'
}