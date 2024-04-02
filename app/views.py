from app import app, db
from flask import request, jsonify, make_response, render_template , send_file
from util.utility import *
from app.models import User, UploadedFile
from werkzeug.security import check_password_hash
from io import BytesIO

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
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({'status': False, 'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email, password=password).first()

    if user:
        # User with provided email and password exists
        # Generate JWT token and set cookie
        token = generate_token(email)
        response = make_response(jsonify({'status': True, 'message': 'Login successful', 'token': token}), 200)
        response.set_cookie('jwt_token', token, httponly=True, secure=True)
        return response
    else:
        # User with provided email and password does not exist
        return render_template('index.html', message='Invalid email or password'), 401
    


@app.route('/')
def index():
    return render_template('index.html')


# API route for uploading PDF files
@app.route('/login/upload', methods=['POST'])
def upload_file():
    keyword = request.form.get('keyword')
    file = request.files['file']
    file_name = file.filename

    if not (keyword and file):
        return jsonify({'error': 'Keyword and file are required.'}), 400

    uploaded_file = UploadedFile(keyword=keyword, file_name=file_name,file_data=file.read())
    db.session.add(uploaded_file)
    db.session.commit()

    return jsonify({'message': 'File uploaded successfully.'})

# download file on basis of keyword
@app.route('/login/download', methods=['GET'])
def download_file():
    keyword = request.args.get('keyword')

    if not keyword:
        return jsonify({'error': 'Keyword is required.'}), 400

    uploaded_file = UploadedFile.query.filter_by(keyword=keyword).first()
    if not uploaded_file:
        return jsonify({'error': 'File not found for the given keyword.'}), 404

    # Convert file data to BytesIO object
    file_stream = BytesIO(uploaded_file.file_data)

    # Send the file data as a response
    return send_file(
        file_stream,
        as_attachment=True,
        download_name=f'{keyword}.pdf',
        mimetype='application/pdf'
    )
    
#list of all files with name , id and keyword    

@app.route('/login/all_files', methods=['GET'])
def list_files():
    partial_keyword = request.args.get('keyword')

    if not partial_keyword:
        return jsonify({'error': 'Keyword is required.'}), 400

    files = UploadedFile.query.filter(UploadedFile.keyword.like(f'{partial_keyword}%')).all()
    files_data = [{'id': file.id, 'keyword': file.keyword,'file_name': file.file_name} for file in files]
    return jsonify(files_data)

