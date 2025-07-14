// Modern Car Rental System - Enhanced JavaScript

// DOM Ready with enhanced initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeAnimations();
    initializeIntersectionObserver();

    // Discount code: require re-validation if changed after validation
    const discountInput = document.getElementById('discount_code');
    if (discountInput) {
        discountInput.addEventListener('input', function() {
            appliedDiscount = null;
            const discountStatusDiv = document.getElementById('discount_status');
            if (discountStatusDiv) discountStatusDiv.style.display = 'none';
        });
    }

    // Notification widget open/close logic for all pages
    const notificationIcon = document.getElementById('notification-icon');
    const notificationPanel = document.getElementById('notification-panel');
    if (notificationIcon && notificationPanel) {
        notificationIcon.addEventListener('click', function() {
            notificationPanel.style.display = (notificationPanel.style.display === 'none' || !notificationPanel.style.display) ? 'block' : 'none';
        });
    }
});

function initializeApp() {
    // Initialize all core functionality
    initTabs();
    initPriceCalculator();
    initBookingSystem();
    initAdminTools();
    initFormValidation();
    initEnhancedFormValidation(); // Add enhanced form validation
    initTooltips();
    initProgressiveEnhancement();
    
    // Add loading states
    removeInitialLoadingStates();
}

// Enhanced Tab Functionality with smooth transitions
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const target = button.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.style.transform = 'scale(1)';
            });
            tabContents.forEach(content => {
                content.classList.remove('active');
                content.style.opacity = '0';
            });
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            button.style.transform = 'scale(1.02)';
            
            const targetContent = document.getElementById(target);
            if (targetContent) {
                setTimeout(() => {
                    targetContent.classList.add('active');
                    targetContent.style.opacity = '1';
                    targetContent.style.transform = 'translateY(0)';
                }, 150);
            }
        });
    });
}

// Enhanced Price Calculator with debouncing and loading states
function initPriceCalculator() {
    const vehicleSelect = document.getElementById('vehicle_id');
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const priceDisplay = document.getElementById('price-display');
    
    if (vehicleSelect && startDateInput && endDateInput) {
        const inputs = [vehicleSelect, startDateInput, endDateInput];
        
        // Debounced price calculation
        const debouncedCalculatePrice = debounce(calculatePrice, 500);
        
        inputs.forEach(input => {
            input.addEventListener('change', debouncedCalculatePrice);
            input.addEventListener('input', debouncedCalculatePrice);
        });
    }
}

// Enhanced price calculation with better error handling and animations
async function calculatePrice() {
    const vehicleId = document.getElementById('vehicle_id')?.value;
    const startDate = document.getElementById('start_date')?.value;
    const endDate = document.getElementById('end_date')?.value;
    const priceDisplay = document.getElementById('price-display');
    
    console.log('calculatePrice called with:', { vehicleId, startDate, endDate });
    
    if (!vehicleId || !startDate || !endDate || !priceDisplay) {
        console.log('Missing required fields:', { vehicleId, startDate, endDate, priceDisplay: !!priceDisplay });
        return;
    }
    
    try {
        showLoadingState(priceDisplay);
        
        const requestData = {
            vehicle_id: vehicleId,
            start_date: startDate,
            end_date: endDate
        };
        
        console.log('Sending request to /api/calculate_price:', requestData);
        
        const response = await fetch('/api/calculate_price', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Response error:', errorText);
            throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.price) {
            displayPrice(priceDisplay, data.price, startDate, endDate);
        } else {
            showError(priceDisplay, data.error || 'Unable to calculate price');
        }
    } catch (error) {
        console.error('Price calculation error:', error);
        showError(priceDisplay, 'Error calculating price. Please try again.');
    }
}

function displayPrice(container, price, startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const hours = Math.ceil((end - start) / (1000 * 60 * 60));
    
    let originalPrice = price;
    let discountAmount = 0;
    let finalPrice = price;
    
    // Apply discount if available
    if (appliedDiscount) {
        discountAmount = price * (appliedDiscount.percentage / 100);
        finalPrice = price - discountAmount;
    }
    
    let priceHtml = `
        <div class="pricing-display" style="opacity: 0; transform: translateY(20px);">
            <div class="price-amount">₹${finalPrice.toFixed(2)}</div>
            <div class="price-details">
                Total for ${hours} hour${hours !== 1 ? 's' : ''}
                <br>
                <small>Includes dynamic pricing adjustments</small>
    `;
    
    if (appliedDiscount) {
        priceHtml += `
                <br>
                <div style="margin-top: var(--space-2); padding: var(--space-2); background: var(--success-50); border-radius: var(--radius-md); border: 1px solid var(--success-200);">
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: var(--text-sm);">
                        <span>Original Price:</span>
                        <span>₹${originalPrice.toFixed(2)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: var(--text-sm); color: var(--success-600); font-weight: 600;">
                        <span>Discount (${appliedDiscount.percentage}%):</span>
                        <span>-₹${discountAmount.toFixed(2)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: var(--text-sm); font-weight: 700; margin-top: var(--space-1);">
                        <span>Final Price:</span>
                        <span>₹${finalPrice.toFixed(2)}</span>
                    </div>
                </div>
        `;
    }
    
    priceHtml += `
            </div>
        </div>
    `;
    
    container.innerHTML = priceHtml;
    container.classList.remove('hidden');
    
    // Animate in
    setTimeout(() => {
        const pricingDisplay = container.querySelector('.pricing-display');
        pricingDisplay.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
        pricingDisplay.style.opacity = '1';
        pricingDisplay.style.transform = 'translateY(0)';
    }, 50);
}

function showLoadingState(container) {
    container.innerHTML = `
        <div class="pricing-display loading" style="opacity: 0;">
            <div class="price-amount shimmer">Calculating...</div>
            <div class="price-details">Please wait</div>
        </div>
    `;
    container.classList.remove('hidden');
    
    setTimeout(() => {
        const pricingDisplay = container.querySelector('.pricing-display');
        pricingDisplay.style.transition = 'opacity 0.3s ease';
        pricingDisplay.style.opacity = '1';
    }, 50);
}

function showError(container, message) {
    container.innerHTML = `
        <div class="alert alert-error" style="opacity: 0; transform: translateY(10px);">
            ${message}
        </div>
    `;
    
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        alert.style.transition = 'all 0.3s ease';
        alert.style.opacity = '1';
        alert.style.transform = 'translateY(0)';
    }, 50);
}

// Enhanced Booking System with progress indicators
function initBookingSystem() {
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', handleBookingSubmission);
    }
    
    // Enhanced discount code validation with apply button
    const discountInput = document.getElementById('discount_code');
    const applyDiscountBtn = document.getElementById('apply_discount_btn');
    
    if (discountInput) {
        // Remove auto-validation on input/blur, only validate when Apply button is clicked
        if (applyDiscountBtn) {
            applyDiscountBtn.addEventListener('click', validateDiscountCode);
        }
    }
}

async function handleBookingSubmission(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    // Enhanced loading state
    submitButton.disabled = true;
    submitButton.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div class="loading-spinner"></div>
            Processing...
        </div>
    `;
    
    addLoadingSpinnerStyles();

    // --- Custom validation for start/end date relationship ---
    const startDate = formData.get('start_date');
    const endDate = formData.get('end_date');
    const startInput = document.getElementById('start_date');
    const endInput = document.getElementById('end_date');
    clearFieldError(startInput);
    clearFieldError(endInput);
    if (startDate && endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        if (end <= start) {
            showFieldError(endInput, 'End date/time must be after start date/time');
            showFieldError(startInput, '');
            showErrorMessage('End date/time must be after start date/time');
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
            return;
        }
    }
    // --- End custom validation ---

    // --- Discount code robust validation ---
    const discountInput = document.getElementById('discount_code');
    const discountStatusDiv = document.getElementById('discount_status');
    const code = discountInput.value.trim();
    // If a code is entered, ensure it is validated and valid
    if (code) {
        // If no appliedDiscount or code changed after validation, force validation
        if (!appliedDiscount || appliedDiscount.code !== code) {
            // Show loading state
            showFieldLoading(discountInput);
            if (discountStatusDiv) discountStatusDiv.style.display = 'none';
            try {
                // Get current vehicle info
                const vehicleId = document.getElementById('vehicle_id')?.value;
                const vehicleSelect = document.getElementById('vehicle_id');
                const selectedOption = vehicleSelect?.options[vehicleSelect.selectedIndex];
                const vehicleType = selectedOption?.textContent.split('(')[1]?.split(')')[0] || '';
                const response = await fetch('/api/validate_discount', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        discount_code: code,
                        vehicle_id: vehicleId,
                        vehicle_type: vehicleType
                    })
                });
                const data = await response.json();
                if (response.ok && data.valid) {
                    appliedDiscount = {
                        code: data.code,
                        percentage: data.discount_percentage,
                        description: data.description
                    };
                    showFieldSuccess(discountInput, `Valid! ${data.discount_percentage}% discount applied`);
                    if (discountStatusDiv) {
                        discountStatusDiv.innerHTML = `
                            <div class="alert alert-success" style="padding: var(--space-2); border-radius: var(--radius-md); font-size: var(--text-sm);">
                                <strong>✓ Discount Applied:</strong> ${data.discount_percentage}% off - ${data.description || 'Discount applied'}
                            </div>
                        `;
                        discountStatusDiv.style.display = 'block';
                    }
                } else {
                    appliedDiscount = null;
                    showFieldError(discountInput, data.error || 'Invalid or expired discount code');
                    if (discountStatusDiv) discountStatusDiv.style.display = 'none';
                    showErrorMessage(data.error || 'Invalid or expired discount code');
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                    return;
                }
            } catch (error) {
                appliedDiscount = null;
                showFieldError(discountInput, 'Unable to validate discount code');
                if (discountStatusDiv) discountStatusDiv.style.display = 'none';
                showErrorMessage('Unable to validate discount code');
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
                return;
            }
        }
    } else {
        appliedDiscount = null;
        if (discountStatusDiv) discountStatusDiv.style.display = 'none';
    }
    // --- End discount code robust validation ---
    
    try {
        const bookingData = {
            vehicle_id: formData.get('vehicle_id'),
            start_date: formData.get('start_date'),
            end_date: formData.get('end_date'),
            discount_code: appliedDiscount ? appliedDiscount.code : formData.get('discount_code'),
            loyalty_token_id: formData.get('loyalty_token_id')
        };
        
        const response = await fetch('/api/create_booking', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bookingData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage('Booking created successfully! Redirecting...');
            // Animate form out
            event.target.style.transition = 'all 0.5s ease';
            event.target.style.opacity = '0.5';
            event.target.style.transform = 'scale(0.98)';
            setTimeout(() => {
                window.location.href = '/customer/dashboard';
            }, 2000);
        } else {
            // Show backend error message clearly
            showErrorMessage(result.error || 'Booking failed. Please try again.');
            // Optionally highlight fields if error is field-specific
            if (result.error && result.error.toLowerCase().includes('date')) {
                showFieldError(startInput, '');
                showFieldError(endInput, result.error);
            }
            if (result.error && result.error.toLowerCase().includes('vehicle')) {
                const vehicleInput = document.getElementById('vehicle_id');
                if (vehicleInput) showFieldError(vehicleInput, result.error);
            }
            if (result.error && result.error.toLowerCase().includes('discount')) {
                showFieldError(discountInput, result.error);
            }
            if (result.error && result.error.toLowerCase().includes('loyalty')) {
                const loyaltyInput = document.getElementById('loyalty_token_id');
                if (loyaltyInput) showFieldError(loyaltyInput, result.error);
            }
        }
    } catch (error) {
        console.error('Booking error:', error);
        showErrorMessage('An error occurred while creating the booking. Please try again.');
    } finally {
        // Re-enable submit button
        setTimeout(() => {
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        }, 1000);
    }
}

// Global variable to store applied discount
let appliedDiscount = null;

async function validateDiscountCode() {
    const discountInput = document.getElementById('discount_code');
    const applyBtn = document.getElementById('apply_discount_btn');
    const statusDiv = document.getElementById('discount_status');
    const code = discountInput.value.trim();
    
    if (!code) {
        clearFieldValidation(discountInput);
        statusDiv.style.display = 'none';
        appliedDiscount = null;
        return;
    }
    
    // Show loading state
    showFieldLoading(discountInput);
    applyBtn.disabled = true;
    applyBtn.textContent = 'Validating...';
    
    try {
        // Get current vehicle info
        const vehicleId = document.getElementById('vehicle_id')?.value;
        const vehicleSelect = document.getElementById('vehicle_id');
        const selectedOption = vehicleSelect?.options[vehicleSelect.selectedIndex];
        const vehicleType = selectedOption?.textContent.split('(')[1]?.split(')')[0] || '';
        
        const response = await fetch('/api/validate_discount', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                discount_code: code,
                vehicle_id: vehicleId,
                vehicle_type: vehicleType
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.valid) {
            appliedDiscount = {
                code: data.code,
                percentage: data.discount_percentage,
                description: data.description
            };
            
            showFieldSuccess(discountInput, `Valid! ${data.discount_percentage}% discount applied`);
            statusDiv.innerHTML = `
                <div class="alert alert-success" style="padding: var(--space-2); border-radius: var(--radius-md); font-size: var(--text-sm);">
                    <strong>✓ Discount Applied:</strong> ${data.discount_percentage}% off - ${data.description || 'Discount applied'}
                </div>
            `;
            statusDiv.style.display = 'block';
            
            // Recalculate price with discount
            if (window.CarRentalApp && window.CarRentalApp.calculatePrice) {
                window.CarRentalApp.calculatePrice();
            }
        } else {
            appliedDiscount = null;
            showFieldError(discountInput, data.error || 'Invalid or expired discount code');
            statusDiv.style.display = 'none';
        }
    } catch (error) {
        console.error('Discount validation error:', error);
        showFieldError(discountInput, 'Unable to validate discount code');
        statusDiv.style.display = 'none';
        appliedDiscount = null;
    } finally {
        applyBtn.disabled = false;
        applyBtn.textContent = 'Apply';
    }
}

// Enhanced Admin Tools
function initAdminTools() {
    const simulatorForm = document.getElementById('price-simulator-form');
    if (simulatorForm) {
        simulatorForm.addEventListener('submit', handlePriceSimulation);
    }
    
    initVehicleManagement();
    initLoyaltyManagement();
}

async function handlePriceSimulation(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const resultDiv = document.getElementById('simulation-result');
    const submitButton = event.target.querySelector('button[type="submit"]');
    
    // Enhanced loading state
    submitButton.disabled = true;
    submitButton.innerHTML = 'Calculating...';
    
    try {
        const response = await fetch('/admin/simulate_price', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                vehicle_id: formData.get('vehicle_id'),
                start_datetime: formData.get('start_datetime'),
                end_datetime: formData.get('end_datetime')
            })
        });
        
        const result = await response.json();
        
        if (result.simulated_price) {
            resultDiv.innerHTML = `
                <div class="alert alert-success" style="opacity: 0; transform: translateY(10px);">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="font-size: 2rem;">💰</div>
                        <div>
                            <strong>Simulated Price: ₹${result.simulated_price}</strong>
                            <br>
                            <small>This includes all dynamic pricing adjustments</small>
                        </div>
                    </div>
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-error" style="opacity: 0; transform: translateY(10px);">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="font-size: 2rem;">⚠️</div>
                        <div>
                            <strong>Error:</strong> ${result.error || 'Unable to simulate price'}
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Animate result in
        setTimeout(() => {
            const alert = resultDiv.querySelector('.alert');
            alert.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            alert.style.opacity = '1';
            alert.style.transform = 'translateY(0)';
        }, 50);
        
    } catch (error) {
        console.error('Price simulation error:', error);
        resultDiv.innerHTML = `
            <div class="alert alert-error">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 2rem;">❌</div>
                    <div>An error occurred during simulation</div>
                </div>
            </div>
        `;
    } finally {
        submitButton.disabled = false;
        submitButton.innerHTML = 'Simulate Price';
    }
}

function initVehicleManagement() {
    // Enhanced vehicle management with better UX
    document.querySelectorAll('.edit-vehicle-btn').forEach(btn => {
        btn.addEventListener('click', handleEditVehicle);
    });
    
    document.querySelectorAll('.delete-vehicle-btn').forEach(btn => {
        btn.addEventListener('click', handleDeleteVehicle);
    });
}

function initLoyaltyManagement() {
    const issueLoyaltyForm = document.getElementById('issue-loyalty-form');
    if (issueLoyaltyForm) {
        issueLoyaltyForm.addEventListener('submit', handleIssueLoyaltyToken);
    }
}

// Enhanced Animation System
function initializeAnimations() {
    // Stagger animations for better visual flow
    staggerGridAnimations();
    
    // Add hover effects to interactive elements
    addHoverEffects();
    
    // Initialize scroll-triggered animations
    initScrollAnimations();
}

function initializeIntersectionObserver() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('fade-in-up');
                }, index * 100); // Stagger the animations
            }
        });
    }, observerOptions);
    
    // Observe all animatable elements
    document.querySelectorAll('.card, .vehicle-card, .stat-card, .table-container').forEach(el => {
        observer.observe(el);
    });
}

function staggerGridAnimations() {
    const grids = document.querySelectorAll('.grid, .stats-grid');
    
    grids.forEach(grid => {
        const items = Array.from(grid.children);
        items.forEach((item, index) => {
            item.style.animationDelay = `${index * 0.1}s`;
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                item.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, index * 100);
        });
    });
}

function addHoverEffects() {
    // Enhanced button hover effects
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Enhanced card hover effects
    document.querySelectorAll('.card, .vehicle-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

function initScrollAnimations() {
    // Parallax effect for background elements
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallax = document.querySelector('body::before');
        
        // Update CSS custom property for scroll-based animations
        document.documentElement.style.setProperty('--scroll', scrolled * 0.5 + 'px');
    });
}

// Enhanced Form Validation
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], select[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => {
                clearFieldError(input);
                if (input.value.trim()) {
                    validateField(input);
                }
            });
        });
        
        // Real-time form validation
        form.addEventListener('input', () => {
            updateFormValidationState(form);
        });
    });
}

// Enhanced frontend validation functions
function validateBookingForm() {
    const vehicleId = document.getElementById('vehicle_id')?.value;
    const startDate = document.getElementById('start_date')?.value;
    const endDate = document.getElementById('end_date')?.value;
    const discountCode = document.getElementById('discount_code')?.value;
    
    const errors = [];
    
    // Validate vehicle selection
    if (!vehicleId) {
        errors.push('Please select a vehicle');
    }
    
    // Validate dates
    if (!startDate) {
        errors.push('Please select a start date and time');
    }
    
    if (!endDate) {
        errors.push('Please select an end date and time');
    }
    
    if (startDate && endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        const now = new Date();
        
        if (start < now) {
            errors.push('Start date cannot be in the past');
        }
        
        if (end <= start) {
            errors.push('End date must be after start date');
        }
        
        // Check if booking is not more than 30 days in advance
        const thirtyDaysFromNow = new Date();
        thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);
        
        if (start > thirtyDaysFromNow) {
            errors.push('Bookings cannot be made more than 30 days in advance');
        }
        
        // Check minimum booking duration (1 hour)
        const durationHours = (end - start) / (1000 * 60 * 60);
        if (durationHours < 1) {
            errors.push('Minimum booking duration is 1 hour');
        }
    }
    
    // Validate discount code format
    if (discountCode && discountCode.length > 50) {
        errors.push('Discount code is too long');
    }
    
    return errors;
}

function validateEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

function validatePassword(password) {
    const errors = [];
    
    if (password.length < 8) {
        errors.push('Password must be at least 8 characters long');
    }
    
    if (!/[A-Z]/.test(password)) {
        errors.push('Password must contain at least one uppercase letter');
    }
    
    if (!/[a-z]/.test(password)) {
        errors.push('Password must contain at least one lowercase letter');
    }
    
    if (!/\d/.test(password)) {
        errors.push('Password must contain at least one number');
    }
    
    return errors;
}

function validateRegistrationForm() {
    const email = document.getElementById('email')?.value?.trim();
    const password = document.getElementById('password')?.value;
    const fullName = document.getElementById('full_name')?.value?.trim();
    
    const errors = [];
    
    if (!email) {
        errors.push('Email is required');
    } else if (!validateEmail(email)) {
        errors.push('Please enter a valid email address');
    }
    
    if (!password) {
        errors.push('Password is required');
    } else {
        const passwordErrors = validatePassword(password);
        errors.push(...passwordErrors);
    }
    
    if (!fullName) {
        errors.push('Full name is required');
    } else if (fullName.length < 2 || fullName.length > 100) {
        errors.push('Full name must be between 2 and 100 characters');
    }
    
    return errors;
}

function validateLoginForm() {
    const email = document.getElementById('email')?.value?.trim();
    const password = document.getElementById('password')?.value;
    
    const errors = [];
    
    if (!email) {
        errors.push('Email is required');
    } else if (!validateEmail(email)) {
        errors.push('Please enter a valid email address');
    }
    
    if (!password) {
        errors.push('Password is required');
    }
    
    return errors;
}

// Enhanced form validation with real-time feedback
function initEnhancedFormValidation() {
    // Booking form validation
    const bookingForm = document.querySelector('form[data-form="booking"]');
    if (bookingForm) {
        const inputs = bookingForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => clearFieldError(input));
        });
        
        bookingForm.addEventListener('submit', (e) => {
            const errors = validateBookingForm();
            if (errors.length > 0) {
                e.preventDefault();
                showErrorMessage(errors.join('<br>'));
                return false;
            }
        });
    }
    
    // Registration form validation
    const registrationForm = document.querySelector('form[data-form="registration"]');
    if (registrationForm) {
        const inputs = registrationForm.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => clearFieldError(input));
        });
        
        registrationForm.addEventListener('submit', (e) => {
            const errors = validateRegistrationForm();
            if (errors.length > 0) {
                e.preventDefault();
                showErrorMessage(errors.join('<br>'));
                return false;
            }
        });
    }
    
    // Login form validation
    const loginForm = document.querySelector('form[data-form="login"]');
    if (loginForm) {
        const inputs = loginForm.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => clearFieldError(input));
        });
        
        loginForm.addEventListener('submit', (e) => {
            const errors = validateLoginForm();
            if (errors.length > 0) {
                e.preventDefault();
                showErrorMessage(errors.join('<br>'));
                return false;
            }
        });
    }
}

// Enhanced field validation with specific rules
function validateField(field) {
    const fieldType = field.type;
    const fieldName = field.name;
    const value = field.value.trim();
    
    clearFieldError(field);
    
    // Email validation
    if (fieldType === 'email' || fieldName === 'email') {
        if (value && !validateEmail(value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }
    
    // Password validation
    if (fieldType === 'password' || fieldName === 'password') {
        if (value) {
            const passwordErrors = validatePassword(value);
            if (passwordErrors.length > 0) {
                showFieldError(field, passwordErrors[0]);
                return false;
            }
        }
    }
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        const fieldLabel = field.getAttribute('placeholder') || fieldName;
        showFieldError(field, `${fieldLabel} is required`);
        return false;
    }
    
    // Date validation for booking
    if (fieldName === 'start_date' || fieldName === 'end_date') {
        if (value) {
            const date = new Date(value);
            const now = new Date();
            
            if (fieldName === 'start_date' && date < now) {
                showFieldError(field, 'Start date cannot be in the past');
                return false;
            }
            
            if (fieldName === 'end_date') {
                const startDate = document.getElementById('start_date')?.value;
                if (startDate && date <= new Date(startDate)) {
                    showFieldError(field, 'End date must be after start date');
                    return false;
                }
            }
        }
    }
    
    showFieldSuccess(field);
    return true;
}

function updateFormValidationState(form) {
    const inputs = form.querySelectorAll('input[required], select[required]');
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        const allValid = Array.from(inputs).every(input => {
            return input.value.trim() && !input.classList.contains('error');
        });
        
        submitButton.disabled = !allValid;
        submitButton.style.opacity = allValid ? '1' : '0.6';
    }
}

function showFieldError(field, message) {
    clearFieldValidation(field);
    
    field.classList.add('error');
    field.style.borderColor = '#ef4444';
    field.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem; color: #ef4444; font-size: 0.875rem; margin-top: 0.5rem;">
            <span>⚠️</span>
            <span>${message}</span>
        </div>
    `;
    
    field.parentNode.appendChild(errorDiv);
}

function showFieldSuccess(field, message = '') {
    clearFieldValidation(field);
    
    field.classList.add('success');
    field.style.borderColor = '#22c55e';
    field.style.boxShadow = '0 0 0 3px rgba(34, 197, 94, 0.1)';
    
    if (message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'field-success';
        successDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem; color: #22c55e; font-size: 0.875rem; margin-top: 0.5rem;">
                <span>✅</span>
                <span>${message}</span>
            </div>
        `;
        
        field.parentNode.appendChild(successDiv);
    }
}

function showFieldWarning(field, message) {
    clearFieldValidation(field);
    
    field.classList.add('warning');
    field.style.borderColor = '#f59e0b';
    field.style.boxShadow = '0 0 0 3px rgba(245, 158, 11, 0.1)';
    
    const warningDiv = document.createElement('div');
    warningDiv.className = 'field-warning';
    warningDiv.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem; color: #f59e0b; font-size: 0.875rem; margin-top: 0.5rem;">
            <span>💡</span>
            <span>${message}</span>
        </div>
    `;
    
    field.parentNode.appendChild(warningDiv);
}

function showFieldLoading(field) {
    clearFieldValidation(field);
    
    field.style.borderColor = '#6b7280';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'field-loading';
    loadingDiv.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.875rem; margin-top: 0.5rem;">
            <div class="loading-spinner" style="width: 16px; height: 16px;"></div>
            <span>Validating...</span>
        </div>
    `;
    
    field.parentNode.appendChild(loadingDiv);
}

function clearFieldValidation(field) {
    field.classList.remove('error', 'success', 'warning');
    field.style.borderColor = '';
    field.style.boxShadow = '';
    
    const existingFeedback = field.parentNode.querySelectorAll('.field-error, .field-success, .field-warning, .field-loading');
    existingFeedback.forEach(el => el.remove());
}

function clearFieldError(field) {
    clearFieldValidation(field);
}

// Enhanced Toast System
function showSuccessMessage(message) {
    showToast(message, 'success', '✅');
}

function showErrorMessage(message) {
    showToast(message, 'error', '❌');
}

function showWarningMessage(message) {
    showToast(message, 'warning', '⚠️');
}

function showToast(message, type = 'info', icon = 'ℹ️') {
    // Remove existing toasts
    document.querySelectorAll('.toast').forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.25rem;">${icon}</span>
                <span>${message}</span>
            </div>
            <button class="toast-close">&times;</button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    }, 50);
    
    // Auto remove after 5 seconds
    const autoRemoveTimer = setTimeout(() => {
        removeToast(toast);
    }, 5000);
    
    // Manual close
    toast.querySelector('.toast-close').addEventListener('click', () => {
        clearTimeout(autoRemoveTimer);
        removeToast(toast);
    });
    
    // Pause auto-remove on hover
    toast.addEventListener('mouseenter', () => clearTimeout(autoRemoveTimer));
    toast.addEventListener('mouseleave', () => {
        setTimeout(() => removeToast(toast), 2000);
    });
}

function removeToast(toast) {
    toast.style.transform = 'translateX(100%)';
    toast.style.opacity = '0';
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

// Enhanced Modal System
function showModal(content, options = {}) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: ${options.maxWidth || '600px'};">
            ${content}
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    
    // Show modal with animation
    setTimeout(() => {
        modal.classList.add('show');
    }, 50);
    
    // Close modal handlers
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal(modal);
        }
    });
    
    modal.querySelector('.modal-close').addEventListener('click', () => {
        closeModal(modal);
    });
    
    // ESC key handler
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            closeModal(modal);
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
    
    return modal;
}

function closeModal(modal) {
    modal.classList.remove('show');
    document.body.style.overflow = '';
    
    setTimeout(() => {
        if (modal.parentNode) {
            modal.parentNode.removeChild(modal);
        }
    }, 300);
}

// Enhanced Modal System (additions)
function showConfirmModal({ title = 'Are you sure?', message = '', confirmText = 'Confirm', cancelText = 'Cancel', onConfirm, onCancel, danger = false }) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 400px;">
            <h3 class="modal-title" style="margin-bottom: 1rem; color: ${danger ? 'var(--error-500)' : 'var(--accent-main)'};">${title}</h3>
            <div style="margin-bottom: 2rem; color: var(--neutral-700);">${message}</div>
            <div style="display: flex; gap: 1rem; justify-content: center;">
                <button class="btn ${danger ? 'btn-danger' : 'btn-primary'} modal-confirm">${confirmText}</button>
                <button class="btn btn-outline modal-cancel">${cancelText}</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
    setTimeout(() => modal.classList.add('show'), 50);
    // Focus first button
    setTimeout(() => modal.querySelector('.modal-confirm').focus(), 100);
    // Handlers
    modal.querySelector('.modal-confirm').onclick = () => {
        closeModal(modal);
        if (onConfirm) onConfirm();
    };
    modal.querySelector('.modal-cancel').onclick = () => {
        closeModal(modal);
        if (onCancel) onCancel();
    };
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal(modal);
    });
    // ESC key
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            closeModal(modal);
            document.removeEventListener('keydown', escHandler);
            if (onCancel) onCancel();
        }
    };
    document.addEventListener('keydown', escHandler);
    return modal;
}

// Custom Dropdown System
function customDropdown(select) {
    if (!select || select.dataset.customized) return;
    select.style.display = 'none';
    select.dataset.customized = 'true';
    const wrapper = document.createElement('div');
    wrapper.className = 'custom-dropdown';
    wrapper.tabIndex = 0;
    wrapper.setAttribute('role', 'listbox');
    wrapper.style.position = 'relative';
    wrapper.style.width = select.offsetWidth + 'px';
    // Button
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'custom-dropdown-btn';
    button.innerHTML = select.options[select.selectedIndex]?.textContent || 'Select...';
    button.setAttribute('aria-haspopup', 'listbox');
    button.setAttribute('aria-expanded', 'false');
    // List
    const list = document.createElement('ul');
    list.className = 'custom-dropdown-list';
    list.style.display = 'none';
    list.setAttribute('role', 'listbox');
    // Populate
    Array.from(select.options).forEach((opt, i) => {
        const li = document.createElement('li');
        li.className = 'custom-dropdown-item';
        li.setAttribute('role', 'option');
        li.tabIndex = -1;
        li.textContent = opt.textContent;
        if (opt.selected) li.classList.add('selected');
        li.onclick = () => {
            select.selectedIndex = i;
            button.innerHTML = opt.textContent;
            list.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
            li.classList.add('selected');
            list.style.display = 'none';
            button.setAttribute('aria-expanded', 'false');
            select.dispatchEvent(new Event('change'));
        };
        list.appendChild(li);
    });
    // Show/hide
    button.onclick = (e) => {
        e.stopPropagation();
        const isOpen = list.style.display === 'block';
        document.querySelectorAll('.custom-dropdown-list').forEach(l => l.style.display = 'none');
        list.style.display = isOpen ? 'none' : 'block';
        button.setAttribute('aria-expanded', !isOpen);
        if (!isOpen) setTimeout(() => list.querySelector('.selected')?.focus(), 100);
    };
    // Keyboard nav
    wrapper.addEventListener('keydown', (e) => {
        const items = Array.from(list.children);
        let idx = items.findIndex(item => item === document.activeElement);
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (idx < items.length - 1) items[idx + 1].focus();
            else items[0].focus();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (idx > 0) items[idx - 1].focus();
            else items[items.length - 1].focus();
        } else if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            document.activeElement.click();
        } else if (e.key === 'Escape') {
            list.style.display = 'none';
            button.setAttribute('aria-expanded', 'false');
            button.focus();
        }
    });
    // Click outside
    document.addEventListener('click', (e) => {
        if (!wrapper.contains(e.target)) {
            list.style.display = 'none';
            button.setAttribute('aria-expanded', 'false');
        }
    });
    // Assemble
    wrapper.appendChild(button);
    wrapper.appendChild(list);
    select.parentNode.insertBefore(wrapper, select);
}

// Enhance all selects on DOMContentLoaded
addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('select.form-select').forEach(customDropdown);
});

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function formatDate(dateString) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(dateString));
}

function addLoadingSpinnerStyles() {
    if (!document.querySelector('#loading-spinner-styles')) {
        const style = document.createElement('style');
        style.id = 'loading-spinner-styles';
        style.textContent = `
            .loading-spinner {
                width: 20px;
                height: 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top-color: currentColor;
                animation: spin 1s ease-in-out infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
}

function initTooltips() {
    // Simple tooltip system
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.target;
    const text = element.getAttribute('data-tooltip');
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 0.5rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        z-index: 1000;
        pointer-events: none;
        opacity: 0;
        transform: translateY(10px);
        transition: all 0.2s ease;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.bottom + 8 + 'px';
    
    setTimeout(() => {
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'translateY(0)';
    }, 50);
    
    element._tooltip = tooltip;
}

function hideTooltip(event) {
    const element = event.target;
    if (element._tooltip) {
        element._tooltip.style.opacity = '0';
        element._tooltip.style.transform = 'translateY(10px)';
        setTimeout(() => {
            if (element._tooltip && element._tooltip.parentNode) {
                element._tooltip.parentNode.removeChild(element._tooltip);
            }
            element._tooltip = null;
        }, 200);
    }
}

function initProgressiveEnhancement() {
    // Add enhanced features for modern browsers
    if ('IntersectionObserver' in window) {
        // Lazy loading for images
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Service worker registration removed as not needed
    // if ('serviceWorker' in navigator) {
    //   navigator.serviceWorker.register('/sw.js')
    //     .then(function(registration) {
    //       // Registration successful
    //     })
    //     .catch(function(error) {
    //       // Registration failed
    //     });
    // }
}

function removeInitialLoadingStates() {
    // Remove any initial loading states
    document.querySelectorAll('.initial-loading').forEach(el => {
        el.classList.remove('initial-loading');
    });
    
    // Add loaded class to body
    document.body.classList.add('loaded');
}

function payForBooking(bookingId) {
    if (!bookingId) return;
    const btn = document.querySelector(`button[onclick="payForBooking(${bookingId})"]`);
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="loading-spinner"></span> Processing...';
    }
    fetch('/api/pay_for_booking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ booking_id: bookingId })
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showToast('Payment successful! Booking confirmed.', 'success');
            setTimeout(() => window.location.reload(), 1200);
        } else {
            showToast(result.error || 'Payment failed.', 'error');
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = 'Pay Now';
            }
        }
    })
    .catch(() => {
        showToast('Payment error. Please try again.', 'error');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = 'Pay Now';
        }
    });
}

function showPaymentModal(bookingId) {
    const content = `
        <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-6);">
            <div class="modal-title" style="font-size: var(--text-xl); font-weight: 800; color: var(--accent-main); display: flex; align-items: center; gap: var(--space-2);">Payment</div>
            <button class="modal-close" style="background: none; border: none; font-size: 1.5rem; color: var(--neutral-400); cursor: pointer; transition: color var(--transition-fast);" onclick="closeModal(this.closest('.modal'))">&times;</button>
        </div>
        <div style="padding: 0 0 1.5rem 0; display: flex; flex-direction: column; gap: 1.5rem; align-items: center; background: #fff; border-radius: var(--radius-2xl);">
            <div style="display: flex; flex-direction: column; gap: 1.2rem; width: 100%; max-width: 340px;">
                <button class="payment-method-card" data-method="card" style="display: flex; align-items: center; gap: 1rem; background: var(--neutral-100); border: 2px solid var(--primary-200); border-radius: var(--radius-xl); padding: 1.1rem 1.2rem; font-size: 1.1rem; font-weight: 600; color: var(--primary-600); cursor: pointer; transition: box-shadow 0.2s, border-color 0.2s; box-shadow: 0 2px 8px rgba(37,99,235,0.04);">
                    <span style="font-size: 1.7rem;">💳</span> Credit/Debit Card
                </button>
                <button class="payment-method-card" data-method="upi" style="display: flex; align-items: center; gap: 1rem; background: var(--neutral-100); border: 2px solid var(--primary-200); border-radius: var(--radius-xl); padding: 1.1rem 1.2rem; font-size: 1.1rem; font-weight: 600; color: var(--primary-600); cursor: pointer; transition: box-shadow 0.2s, border-color 0.2s; box-shadow: 0 2px 8px rgba(16,185,129,0.04);">
                    <span style="font-size: 1.7rem;">🇮🇳</span> UPI
                </button>
                <button class="payment-method-card" data-method="netbanking" style="display: flex; align-items: center; gap: 1rem; background: var(--neutral-100); border: 2px solid var(--primary-200); border-radius: var(--radius-xl); padding: 1.1rem 1.2rem; font-size: 1.1rem; font-weight: 600; color: var(--primary-600); cursor: pointer; transition: box-shadow 0.2s, border-color 0.2s; box-shadow: 0 2px 8px rgba(59,130,246,0.04);">
                    <span style="font-size: 1.7rem;">🏦</span> Netbanking
                </button>
            </div>
            <div id="payment-processing" style="display:none; margin-top:2rem; text-align:center; width:100%; min-height: 48px;"></div>
        </div>
        <style>
            .payment-method-card:hover {
                background: var(--accent-50) !important;
                border-color: var(--accent-main) !important;
                color: var(--accent-main) !important;
                box-shadow: 0 4px 16px rgba(111,191,115,0.10) !important;
            }
            .modal-content { font-family: var(--font-body); }
            @media (max-width: 600px) {
                .modal-content { padding: var(--space-4) !important; }
            }
        </style>
    `;
    const modal = showModal(content, { maxWidth: '420px' });
    // Add event listeners for payment method buttons
    modal.querySelectorAll('.payment-method-card').forEach(btn => {
        btn.onclick = function() {
            const method = btn.getAttribute('data-method');
            const processingDiv = modal.querySelector('#payment-processing');
            processingDiv.style.display = 'block';
            processingDiv.innerHTML = `<div class='loading-spinner' style='margin-bottom:1rem;'></div><span style='font-size:1.1rem;'>Processing <b>${method === 'card' ? 'Card' : method === 'upi' ? 'UPI' : 'Netbanking'}</b> payment...</span>`;
            // Simulate payment processing delay
            setTimeout(() => {
                processingDiv.innerHTML = `<span style='color:var(--success-500); font-size:2.2rem;'>✔️</span><div style='font-size:1.1rem; margin-top:0.5rem;'>Payment successful!</div>`;
                setTimeout(() => {
                    closeModal(modal);
                    payForBooking(bookingId);
                }, 1100);
            }, 1800);
        };
    });
}

// Enhance booking status feedback
function showStatusToast(status, context) {
    switch (status) {
        case 'approved':
            showToast('Booking approved! Please pay to confirm your booking.', 'info');
            break;
        case 'paid':
            showToast('Payment successful! Booking confirmed.', 'success');
            break;
        case 'completed':
            showToast('Booking marked as completed. Thank you!', 'success');
            break;
        case 'rejected':
            showToast('Booking was rejected by admin.', 'error');
            break;
        case 'cancelled':
            showToast('Booking was cancelled.', 'error');
            break;
        default:
            if (context && context.error) showToast(context.error, 'error');
            break;
    }
}

// --- Ensure booking management handlers are globally available ---
window.showBookingDetails = function(bookingId) {
    fetch(`/api/bookings/${bookingId}`)
        .then(response => response.text())
        .then(html => {
            window.showModal(html, { maxWidth: '600px' });
        })
        .catch(() => window.showToast('Failed to load booking details', 'error'));
};

window.updateBookingStatus = function(bookingId, status) {
    window.showConfirmModal({
        title: `Change Booking Status`,
        message: `Are you sure you want to <b>${status}</b> this booking?`,
        confirmText: 'Yes',
        cancelText: 'No',
        danger: status === 'rejected' || status === 'cancelled',
        onConfirm: function() {
            fetch(`/api/bookings/${bookingId}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            })
            .then(r => r.json())
            .then(result => {
                if (result.success) {
                    window.showToast('Booking status updated!', 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    window.showToast(result.error || 'Failed to update booking status', 'error');
                }
            })
            .catch(() => window.showToast('Network error', 'error'));
        }
    });
};

// Ensure modal and toast helpers are global
window.showModal = showModal;
window.showConfirmModal = showConfirmModal;
window.showToast = showToast;

// Patch payForBooking to show toast for payment
const originalPayForBooking = window.payForBooking;
window.payForBooking = function(bookingId) {
    if (!bookingId) return;
    const btn = document.querySelector(`button[onclick="payForBooking(${bookingId})"]`);
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="loading-spinner"></span> Processing...';
    }
    fetch('/api/pay_for_booking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ booking_id: bookingId })
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showStatusToast('paid');
            setTimeout(() => window.location.reload(), 1200);
        } else {
            showStatusToast('error', result);
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = 'Pay Now';
            }
        }
    })
    .catch(() => {
        showToast('Payment error. Please try again.', 'error');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = 'Pay Now';
        }
    });
};

// Export functions for use in templates
window.CarRentalApp = {
    calculatePrice,
    validateDiscountCode,
    showSuccessMessage,
    showErrorMessage,
    showWarningMessage,
    showModal,
    closeModal,
    formatCurrency,
    formatDate,
    validateField,
    debounce,
    throttle
};