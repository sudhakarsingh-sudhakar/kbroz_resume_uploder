from app import app, db
from flask import request, jsonify, make_response, render_template , send_file, redirect, url_for, flash
from util.utility import *
from app.models import User, UploadedFile
from werkzeug.security import check_password_hash
from io import BytesIO



SEARCH =  None
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
        print(response)
        # return redirect(url_for('index'))
        return render_template('homepage.html', token = token)
        #return response
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
    user = request.form.get("user")
    file = request.files['file']
    file_name = file.filename
    print(f"name : {user} , keyword : {keyword}, filename : {file_name}")

    if not (keyword and file):
        # return jsonify({'error': 'Keyword and file are required.'}), 400
        return render_template("homepage.html")

    uploaded_file = UploadedFile(keyword=keyword,user = user ,file_name=file_name,file_data=file.read())
    db.session.add(uploaded_file)
    db.session.commit()

    return render_template("homepage.html", message = "file uploaded succesfully")
# download file on basis of keyword
@app.route('/login/download', methods=['GET'])
def download_file():
    id = request.args.get('id')

    if not id:
        return jsonify({'error': 'id is required.'}), 400

    uploaded_file = UploadedFile.query.filter_by(id=id).first()
    if not uploaded_file:
        return jsonify({'error': 'File not found for the given keyword.'}), 404

    # Convert file data to BytesIO object
    file_stream = BytesIO(uploaded_file.file_data)

    # Send the file data as a response
    return send_file(
        file_stream,
        as_attachment=True,
        download_name=f'{id}.pdf',
        mimetype='application/pdf'
    )
    
#list of all files with name , id and keyword    

@app.route('/login/all_files', methods=['GET'])
def list_files():
    partial_keyword = request.args.get('search')
    global SEARCH 
    
    if not partial_keyword:
        flash("please provide a vaild keyword")
        #return jsonify({'error': 'Keyword is required.'}), 400
        return render_template("homepage.html")
    
    SEARCH = partial_keyword

    files = UploadedFile.query.filter(UploadedFile.keyword.like(f'{partial_keyword}%')).all()
    files_data = [{'id': file.id, 'keyword': file.keyword,'file_name': file.file_name,'user':file.user} for file in files]
    #return files_data
    return render_template("search_result.html" ,search_results =files_data)



blacklisted_tokens = set()
@app.route('/logout')
def logout():
    # Get the JWT token from the request cookies
    print(request)
    token = request.cookies.get('jwt_token')
    

    if not token:
        return render_template("index.html")


    # Check if the token is blacklisted (optional, depending on your implementation)
    if token in blacklisted_tokens:
        # return jsonify({'status': False, 'message': 'Token already revoked'}), 401
        return render_template("index.html")

    # Add the token to the blacklist (optional)
    blacklisted_tokens.add(token)

    # Remove the JWT token cookie from the response
    response = make_response(jsonify({'status': True, 'message': 'Logout successful'}), 200)
    response.set_cookie('jwt_token', '', expires=0)

    return render_template("index.html")



@app.route('/login/upload_update/<int:id>', methods=['POST'])
def update_file(id):
    print(request.form)
    keyword = request.form.get('keyword')
    user = request.form.get("user")
    file = request.files.get('file')  # Use get() to safely get the file, which can be None
    file_name = request.form.get('file_name')
    print(f"keyword {keyword}")

    # if not (keyword and file):
    #     return jsonify({'error': 'Keyword and file are required.'}), 400

    # Query the database to find the uploaded file record based on the provided id
    uploaded_file = UploadedFile.query.get(id)

    if not uploaded_file:
        flash("uploaded file not find")
        return jsonify({'error': 'Uploaded file not found.'}), 404

    # Update the keyword and name fields if provided
    uploaded_file.keyword = keyword
    uploaded_file.user = user
    uploaded_file.file_name = file_name

    # Update the file data if a new file is provided
    if file:
        uploaded_file.file_name = file.filename
        uploaded_file.file_data = file.read()
    files = UploadedFile.query.filter(UploadedFile.keyword.like(f'{SEARCH}%')).all()
    files_data = [{'id': file.id, 'keyword': file.keyword,'file_name': file.file_name,'user':file.user} for file in files]

    db.session.commit()

    return render_template("search_result.html",  search_results =files_data)


@app.route('/login/delete/<int:id>')
def delete(id):
    uploaded_file = UploadedFile.query.get(id)

    if not uploaded_file:
        flash("uploaded file not find")
        return jsonify({'error': 'Uploaded file not found.'}), 404
    
    # Delete the uploaded file from the database
    db.session.delete(uploaded_file)
    files = UploadedFile.query.filter(UploadedFile.keyword.like(f'{SEARCH}%')).all()
    files_data = [{'id': file.id, 'keyword': file.keyword,'file_name': file.file_name,'user':file.user} for file in files]

    db.session.commit()

    #return jsonify(message= 'Uploaded file deleted successfully.', serach_result= files_data), 200
    return render_template("search_result.html",  search_results =files_data)
    
    
