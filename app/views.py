from app import app, db
from flask import request, jsonify, make_response, render_template
from util.utility import *
from app.models import User
from werkzeug.security import check_password_hash

# def login():
#     data = request.json
#     response_data = {}
#     content = {'status': False, 'message': '', 'data': response_data}
#     is_valid = True

#     try:
#         # Validate email and password presence
#         if 'email' not in data or not data['email']:
#             content['message'] = "Email is required"
#             is_valid = False
#         elif 'password' not in data or not data['password']:
#             content['message'] = "Password is required"
#             is_valid = False
#     except KeyError as e:
#         content['message'] = f"Field required: {e}"
#         is_valid = False

#     if is_valid:
#         email = data['email']
#         password = data['password']

#         # Query the database for the user with the provided email
#         user = User.query.filter_by(email=email).first()

#         if user:
#             # If user exists, check if the password matches
#             if check_password_hash(user.password, password):
#                 # Password matches, generate JWT token
#                 token = generate_token(user.id)  # Assuming user.id is unique
#                 response_data['token'] = token
#                 content['message'] = "Login successful"
#                 content['status'] = True
#             else:
#                 # Password does not match
#                 content['message'] = "Invalid email or password"
#         else:
#             # User with provided email does not exist
#             content['message'] = "Invalid email or password"

#     return jsonify(content)

# def generate_token(email):
#     with app.app_context():
#         # Use a JWT library like PyJWT for secure token generation
#         payload = {
#             'user_email': email,
#             # 'exp': datetime.utcnow() + timedelta(minutes=5)  # Token expires in 5 minutes
#         }
#         return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

# @app.route('/login', methods=['POST'])
# def login_route():
#     data = request.json
#     email = data.get('email')
#     password = data.get('password')

#     if not email or not password:
#         return jsonify({'status': False, 'message': 'Email and password are required'}), 400

#     user = User.query.filter_by(email=email).first()

#     if user:
#         # Check if the user's password matches the provided password
#         if check_password_hash(user.password, password):
#             # Password matches, generate JWT token and set cookie
#             token = generate_token(email)
#             response = make_response(jsonify({'status': True, 'message': 'Login successful'}), 200)
#             response.set_cookie('jwt_token', token, httponly=True, secure=True)
#             return response
#         else:
#             # Password does not match
#             return jsonify({'status': False, 'message': 'Invalid email or password'}), 401
#     else:
#         # User with provided email does not exist
#         return jsonify({'status': False, 'message': 'User not found'}), 404

def login():
    data = request.json
    response_data = {}
    content = {'status': False, 'message': '', 'data': response_data}
    is_valid = True

    try:
        # Validate email and password presence
        if 'email' not in data or not data['email']:
            content['message'] = "Email is required"
            is_valid = False
        elif 'password' not in data or not data['password']:
            content['message'] = "Password is required"
            is_valid = False
    except KeyError as e:
        content['message'] = f"Field required: {e}"
        is_valid = False

    if is_valid:
        email = data['email']
        password = data['password']

        # Query the database for the user with the provided email and password
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            # User with provided email and password exists
            # Generate JWT token
            token = generate_token(user.id)  # Assuming user.id is unique
            response_data['token'] = token
            content['message'] = "Login successful"
            content['status'] = True
        else:
            # User with provided email and password does not exist
            content['message'] = "Invalid email or password"

    return jsonify(content)
def generate_token(email):
    with app.app_context():
        # Use a JWT library like PyJWT for secure token generation
        payload = {
            'user_email': email,
            # 'exp': datetime.utcnow() + timedelta(minutes=5)  # Token expires in 5 minutes
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

@app.route('/login', methods=['POST'])
def login_route():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'status': False, 'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email, password=password).first()

    if user:
        # User with provided email and password exists
        # Generate JWT token and set cookie
        token = generate_token(email)
        response = make_response(jsonify({'status': True, 'message': 'Login successful','token': token}), 200)
        response.set_cookie('jwt_token', token, httponly=True, secure=True)
        return response
    else:
        # User with provided email and password does not exist
        return jsonify({'status': False, 'message': 'Invalid email or password'}), 401
