from flask import Blueprint, request, jsonify
from flask_mail import Message, Mail
import random
import string

main = Blueprint('main', __name__)
mail = Mail()
def generate-otp(length=6)
    characters = string.digits  
    otp = ''.join(random.choice(characters) for i in range(length))
    return otp
otp_store = {}
@main.route('/')
def home():
    return render_template('index.html')

@main.route('/login')
def login():
    data=request.get_json()
    email=data.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400  
    otp = generate_otp()
    try:
        msg = Message("Your OTP Code", recipients=[email])
        msg.body = f"Your OTP is {otp}. It will expire in 5 minutes."
        mail.send(msg)  
        otp_store[email] = otp
        return render_template()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def verify_otp():
    
    data = request.get_json()
    entered_otp = data.get('otp')  # Extract the OTP entered by the user

    if not entered_otp:
        return jsonify({'error': 'Email and OTP are required'}), 400  # Return error if any is missing

    # Step 2: Check if the OTP is stored for the given email
    stored_otp = otp_store.get(email)

    if not stored_otp:
        return jsonify({'error': 'No OTP sent to this email'}), 404  # OTP not found for email

    # Step 3: Compare the entered OTP with the stored one
    if entered_otp == stored_otp:
        return jsonify({'message': 'OTP verified successfully!'}), 200
    else:
        return jsonify({'error': 'Invalid OTP'}), 400
