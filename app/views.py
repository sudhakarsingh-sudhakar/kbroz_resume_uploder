from app import app,db
from flask import request, jsonify, make_response, current_app as app
from flask import render_template
from flask import Flask, request, jsonify
from util.utility import *
from app.models import User  # Import your model class here
from werkzeug.security import check_password_hash


@app.route('/')
def index():
    return render_template('index.html')


#------- login api----------->>>
    

#----------------login

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

        # Query the database for the user with the provided email
        user = User.query.filter_by(email=email).first()

        if user:
            # If user exists, check if the password matches
            if check_password_hash(user.password, password):
                # Password matches, generate JWT token
                token = generate_token(user.id)  # Assuming user.id is unique
                response_data['token'] = token
                content['message'] = "Login successful"
                content['status'] = True
            else:
                # Password does not match
                content['message'] = "Invalid email or password"
        else:
            # User with provided email does not exist
            content['message'] = "Invalid email or password"

    return jsonify(content)

def generate_token(email):
    # Use a JWT library like PyJWT for secure token generation
    payload = {
        'user_email': email,
        # 'exp': datetime.utcnow() + timedelta(minutes=5)  # Token expires in 5 minutes
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

@app.route('/login', methods=['POST'])
def login_route():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        token = generate_token(email)
        response = make_response(jsonify({'status': True, 'message': 'Login successful'}), 200)
        response.set_cookie('jwt_token', token, httponly=True, secure=True)
        return response
    else:
        return jsonify({'status': False, 'message': 'Invalid email or password'}), 401


# @app.route('/')
# def get_all_users():
#     users = User.query.all()
#     serialized_users = []
#     for user in users:
#         serialized_users.append({
#             'id': user.id,
#             'username': user.username,
#             'email': user.email,
#             # Add other fields as needed
#         })
#     return serialized_users
