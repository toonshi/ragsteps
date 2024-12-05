from flask import Blueprint, request, jsonify, render_template
from flask_mail import Message, Mail
import random
import string
import time

main = Blueprint('main', __name__)
mail = Mail()

# Function to generate OTP
def generate_otp(length=6):
    characters = string.digits  
    otp = ''.join(random.choice(characters) for i in range(length))
    return otp

# Store OTPs with their expiration times
otp_store = {}

# Home route
@main.route('/')
def home():
    return render_template('index.html')

# Route to send OTP
@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400  

    otp = generate_otp()
    try:
        msg = Message("Your OTP Code", recipients=[email])
        msg.body = f"Your OTP is {otp}. It will expire in 5 minutes."
        mail.send(msg)  

        # Store OTP with expiration (5 minutes = 300 seconds)
        otp_store[email] = {'otp': otp, 'expires_at': time.time() + 300}

        return jsonify({'message': 'OTP sent successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to verify OTP
@main.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    entered_otp = data.get('otp')

    if not email or not entered_otp:
        return jsonify({'error': 'Email and OTP are required'}), 400  

    # Check if the OTP is stored for the given email
    stored_otp_data = otp_store.get(email)

    if not stored_otp_data:
        return jsonify({'error': 'No OTP sent to this email'}), 404  

    # Check if OTP is expired
    if time.time() > stored_otp_data['expires_at']:
        del otp_store[email]  # Remove expired OTP
        return jsonify({'error': 'OTP has expired'}), 400

    # Compare the entered OTP with the stored one
    if entered_otp == stored_otp_data['otp']:
        del otp_store[email]  # OTP is valid, remove it after successful verification
        return jsonify({'message': 'OTP verified successfully!'}), 200
    else:
        return jsonify({'error': 'Invalid OTP'}), 400
