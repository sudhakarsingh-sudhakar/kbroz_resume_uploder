from app import app, db,create_scoped_session
from flask import request, jsonify, make_response, render_template , send_file, redirect, url_for, flash
from util.utility import *

from app.models import User, UploadedFile
from werkzeug.security import check_password_hash
from io import BytesIO
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError


SEARCH = ""
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

 



# @app.route('/login', methods=['POST', "GET"])
# def login_route():
#     token = request.cookies.get('jwt_token')
#     email = request.form.get('email')
#     password = request.form.get('password')


#     if request.method == "GET" and token :
#         return render_template("homepage.html")


#     if not email or not password:
#         #return jsonify({'status': False, 'message': 'Email and password are required'}), 400
#         return render_template("index.html")

#     user = User.query.filter_by(email=email, password=password).first()

#     if user:
#         # User with provided email and password exists
#         # Generate JWT token and set cookie
#         token = generate_token(email)
#         response = make_response(jsonify({'status': True, 'message': 'Login successful', 'token': token , 'email': email}), 200)
#         print(response)

#         response.set_cookie('jwt_token', token, httponly=True, secure=True)
#         print(response)

#         # return redirect(url_for('index'))
#         return render_template('homepage.html', token = token)
#         #return response
#     else:
#         # User with provided email and password does not exist
#         return render_template('index.html', message='Invalid email or password'), 401
    

    
    

@app.route('/login', methods=['POST', 'GET'])
def login_route():
    try:
        token = request.cookies.get('jwt_token')
        email = request.form.get('email')
        password = request.form.get('password')

        if request.method == "GET" and token:
            return render_template("homepage.html")

        if not email or not password:
            return render_template("index.html")
        with app.app_context():
            scoped_session = create_scoped_session()

            user = scoped_session.query(User).filter_by(email=email, password=password).first()
            scoped_session.close()

            if user:
                token = generate_token(email)
                response = make_response(jsonify({'status': True, 'message': 'Login successful', 'token': token , 'email': email}), 200)
                response.set_cookie('jwt_token', token, httponly=True, secure=True)
                return render_template('homepage.html', token=token)
            else:
                return render_template('index.html', message='Invalid email or password'), 401

    except Exception as e:
        # Log the exception or handle it appropriately
        return render_template('error.html', message='An error occurred. Please try again later.'), 500


@app.route('/')
def index():
    return render_template('index.html')


# # API route for uploading PDF files
# @app.route('/login/upload', methods=['POST'])
# def upload_file():
#     token = request.cookies.get('jwt_token')
#     keyword = request.form.get('keyword')
#     user = request.form.get("username")
#     file = request.files['file']
#     salary = request.form['selectCTC']
#     contact = request.form['contact']
#     email = request.form['email']
#     experience = request.form['selectExperiance']
#     location = request.form['location']
#     file_name = file.filename
#     print(f"name : {user} , keyword : {keyword}, filename : {file_name}, sal  :{ salary}, ctc : {experience , contact , email} ")
#     if not token : 
#         return render_template("index.html")

#     if not (keyword and file) :
#         # return jsonify({'error': 'Keyword and file are required.'}), 400
#         return render_template("homepage.html")
#     with app.app_context():
#         scoped_session = create_scoped_session()
#         uploaded_file = UploadedFile(keyword = keyword, user = user , file_name = file_name , 
#                                  salary = salary, experience =  experience,location = location, 
#                                  email = email, contact = contact, file_data =file.read())
#         db.session.add(uploaded_file)
#         db.session.commit()



    
#     #return render_template("homepage.html",  message ='Your details were successfully received.')
#     # Redirect to a different URL after successful form submission
#     return redirect(url_for('login_route',status_message ='Your details were successfully received.'))


# API route for uploading PDF files
@app.route('/login/upload', methods=['POST'])
def upload_file():
    try:
        token = request.cookies.get('jwt_token')
        keyword = request.form.get('keyword')
        user = request.form.get("username")
        file = request.files['file']
        salary = request.form['selectCTC']
        contact = request.form['contact']
        email = request.form['email']
        experience = request.form['selectExperiance']
        location = request.form['location']
        file_name = file.filename

        # Check if the token is missing
        # if not token:
        #     return render_template("index.html")

        # Check if keyword and file are missing
        if not (keyword and file):
            return render_template("homepage.html")

        with app.app_context():
            # Create a scoped session
            scoped_session = create_scoped_session()
            # Create the UploadedFile object and add it to the session
            uploaded_file = UploadedFile(keyword=keyword, user=user, file_name=file_name,
                                         salary=salary, experience=experience, location=location,
                                         email=email, contact=contact, file_data=file.read())
            scoped_session.add(uploaded_file)
            
            # Commit the changes to the database
            scoped_session.commit()
            scoped_session.close()


        # Redirect to the login route with a success message
        return render_template('homepage.html', status_message='Your details were successfully received.')

    except SQLAlchemyError as e:
        # Handle SQLAlchemy errors
        error_message = str(e)
        return render_template("error.html", message=error_message), 500

    except Exception as e:
        # Handle other exceptions
        error_message = str(e)
        return render_template("error.html", message=error_message), 500


# download file on basis of keyword
@app.route('/login/download', methods=['GET'])
def download_file():
    try:
        token = request.cookies.get('jwt_token')
        id = request.args.get('id')

        if not id:
            return jsonify({'error': 'id is required.'}), 400
        # if not token:
        #     return render_template('index.html')
    
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
        
    except Exception as e:
    #     # Log the exception or handle it appropriately
        
        return render_template({'error.html', 'An error occurred.'}), 500


# app.route('/login/download', methods=['GET'])
# def download_file():
#     try:
#         token = request.cookies.get('jwt_token')
#         id = request.args.get('id')

#         if not id:
#             return jsonify({'error': 'id is required.'}), 400
#         if not token:
#             return render_template('index.html')

#         with app.app_context():
#             scoped_session = create_scoped_session()
#             uploaded_file = scoped_session.query(UploadedFile).filter_by(id=id).first()
#             file_stream = BytesIO(uploaded_file.file_data)
#              # Send the file data as a response
#             return send_file(
#             file_stream,
#             as_attachment=True,
#             download_name=f'{id}.pdf',
#             mimetype='application/pdf'
#         )

       
            

    #     if not uploaded_file:
    #         return jsonify({'error': 'File not found for the given keyword.'}), 404

    #     # Convert file data to BytesIO object
       
    # except Exception as e:
    #     # Log the exception or handle it appropriately
        
    #     return render_template({'error.html', 'An error occurred.'}), 500


# #list of all files with name , id and keyword    

# @app.route('/login/all_files', methods=['GET'])
# def list_files():
#     partial_keyword = request.args.get('keyword')
#     partial_user = request.args.get('user')
#     partial_email = request.args.get('email')
#     partial_contact = request.args.get('contact')
#     partial_location = request.args.get('location')
#     partial_experience = request.args.get('selectExperiance')
#     partial_salary = request.args.get('selectCTC')
#     print(f"partial_keyword  : {partial_keyword} ,, {partial_location},,,defffef,{partial_experience},,,, salary {partial_salary},,,{partial_user}")
#     token = request.cookies.get('jwt_token')
#     print("Received query parameters:")
#     print(f"Keyword: {partial_keyword}")
#     print(f"User: {partial_user}")
#     print(f"Email: {partial_email}")
#     print(f"Contact: {partial_contact}")
#     print(f"Location: {partial_location}")
#     print(f"Experience: {partial_experience}")
#     print(f"Salary: {partial_salary}")
#     global SEARCH 
#     if not token:
#         return render_template('index.html')
#     # if not partial_keyword  or not partial_salary  or not partial_location or not partial_experience:
#     #     flash("please provide a vaild keyword")
#         #return jsonify({'error': 'Keyword is required.'}), 400
#         return render_template("homepage.html")
#     if partial_keyword and partial_experience and partial_salary:
#         files = (UploadedFile.query
#             .filter(and_(
#                 UploadedFile.keyword.like(f'{partial_keyword}%'),
#                 UploadedFile.experience == partial_experience,
#                 UploadedFile.salary == partial_salary
#             ))
#             .all())
#         files_data = [{'id': file.id, 'keyword': file.keyword, 'file_name': file.file_name,
#                    'user': file.user, 'location': file.location, 'salary': file.salary,
#                    'experience': file.experience, 'email': file.email, 'contact': file.contact}
#                   for file in files]
#         return render_template("search_result.html" ,search_results =files_data)

#     SEARCH = partial_keyword

#     files = (UploadedFile.query
#              .filter(and_(
#                  UploadedFile.keyword.like(f'{partial_keyword}%'),
#                  UploadedFile.location.like(f'{partial_location}%'),
#                  UploadedFile.experience == partial_experience,
#                  UploadedFile.salary == partial_salary,
#                  UploadedFile.user.like(f'{partial_user}%'),
#                  UploadedFile.email.like(f'{partial_email}%'),
#                  UploadedFile.contact.like(f'{partial_contact}%')
#              ))
#              .all())
#     print(f"files querry {files}")

#     #files = UploadedFile.query.filter(UploadedFile.keyword.like(f'{partial_keyword}%')).all()
#     files_data = [{'id': file.id, 'keyword': file.keyword, 'file_name': file.file_name,
#                    'user': file.user, 'location': file.location, 'salary': file.salary,
#                    'experience': file.experience, 'email': file.email, 'contact': file.contact}
#                   for file in files]
#     #return files_data
#     if not files_data:
#         return render_template("homepage.html", message = "No files found matching the search criteria.")
#     print(f'files_data: {files_data}')
#     return render_template("search_result.html" ,search_results =files_data)



#API route for listing files based on search criteria
@app.route('/login/all_files', methods=['GET'])
def list_files():
    global SEARCH
    try:
        # Get query parameters from request
        partial_keyword = request.args.get('keyword')
        partial_user = request.args.get('user')
        partial_email = request.args.get('email')
        partial_contact = request.args.get('contact')
        partial_location = request.args.get('location')
        partial_experience = request.args.get('selectExperiance')
        partial_salary = request.args.get('selectCTC')

        print(f"Received query parameters: Keyword: {partial_keyword}, User: {partial_user}, Email: {partial_email}, Contact: {partial_contact}, Location: {partial_location}, Experience: {partial_experience}, Salary: {partial_salary}")

        # Check if JWT token is present
        token = request.cookies.get('jwt_token')
        # if not token:
        #     return render_template('index.html')

        if partial_keyword and partial_experience and partial_salary:
          SEARCH = partial_keyword
          with app.app_context():
            # Create a scoped session
            scoped_session = create_scoped_session()
            files = (scoped_session.query(UploadedFile)
                    .filter(and_(
                        UploadedFile.keyword.like(f'{partial_keyword}%'),
                        UploadedFile.experience == partial_experience,
                        UploadedFile.salary == partial_salary
                    ))
                    .all())
            files_data = [{'id': file.id, 'keyword': file.keyword, 'file_name': file.file_name,
                        'user': file.user, 'location': file.location, 'salary': file.salary,
                        'experience': file.experience, 'email': file.email, 'contact': file.contact}
                        for file in files]
            

        # Check if any files matching the search criteria were found
            if not files_data:
                return render_template("homepage.html", message="No files found matching the search criteria.")
        return render_template("search_result.html" ,search_results =files_data)


    except SQLAlchemyError as e:
        # Handle SQLAlchemy errors
        error_message = str(e)
        return render_template("error.html", message=error_message), 500

    except Exception as e:
        # Handle other exceptions
        error_message = str(e)
        return render_template("error.html", message=error_message), 500


    
    

blacklisted_tokens = set()
@app.route('/logout')
def logout():
    # Get the JWT token from the request cookies
    print(request)
    token = request.cookies.get('jwt_token')
    print(token)
    

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
    token = request.cookies.get('jwt_token')
    keyword = request.form.get('keyword')
    user = request.form.get("user")
    file = request.files['file'] # Use get() to safely get the file, which can be None
    print(file)
    contact = request.form.get('contact')
    location = request.form.get('location')
    email = request.form.get('email')
    file_name = request.form.get('file_name')
    print(f"keyword {keyword}")

    # if not (keyword and file):
    #     return jsonify({'error': 'Keyword and file are required.'}), 400

    # Query the database to find the uploaded file record based on the provided id
    uploaded_file = UploadedFile.query.get(id)
    # if not token:
    #     return render_template('index.html')

    if not uploaded_file:
        flash("uploaded file not find")
        return jsonify({'error': 'Uploaded file not found.'}), 404

    # Update the keyword and name fields if provided
    uploaded_file.keyword = keyword
    uploaded_file.user = user
    uploaded_file.file_name = file_name
    uploaded_file.location = location
    uploaded_file.contact = contact
    uploaded_file.email = email

    # Update the file data if a new file is provided
    if file:
        uploaded_file.file_data = file.read()
        files = UploadedFile.query.filter(UploadedFile.keyword.like(f'{SEARCH}%')).all()
        files_data = [{'id': file.id, 'keyword': file.keyword,'file_name': file.file_name,'user':file.user, 'location':file.location ,'contact'
                   :file.contact , 'email' :file.email,'file_data': uploaded_file.file_data} for file in files]
        db.session.commit()
        return render_template("search_result.html",  search_results =files_data)


    files = UploadedFile.query.filter(UploadedFile.keyword.like(f'{SEARCH}%')).all()
    files_data = [{'id': file.id, 'keyword': file.keyword,'file_name': file.file_name,'user':file.user, 'location':file.location ,'contact'
                   :file.contact , 'email' :file.email} for file in files]

    db.session.commit()

    return render_template("search_result.html",  search_results =files_data)


# # API route for updating a file
# @app.route('/login/upload_update/<int:id>', methods=['POST'])
# def update_file(id):
#     try:
#         # Get form data from the request
#         token = request.cookies.get('jwt_token')
#         keyword = request.form.get('keyword')
#         user = request.form.get("user")
#         file = request.files.get('file')  # Use get() to safely get the file, which can be None
#         contact = request.form.get('contact')
#         location = request.form.get('location')
#         email = request.form.get('email')
#         file_name = request.form.get('file_name')

#         # Query the database to find the uploaded file record based on the provided id
#         with app.app_context():
#             scoped_session = create_scoped_session()
#             uploaded_file =scoped_session.query(UploadedFile).get(id)
    
#         if not token:
#             return render_template('index.html')

#         if not uploaded_file:
#             flash("Uploaded file not found")
#             return jsonify({'error': 'Uploaded file not found.'}), 404

#         # Update the fields of the uploaded file record if provided
#         uploaded_file.keyword = keyword
#         uploaded_file.user = user
#         uploaded_file.file_name = file_name
#         uploaded_file.location = location
#         uploaded_file.contact = contact
#         uploaded_file.email = email

#         # Handle file update if a new file is provided
#         if file:
#             # Handle file update if a new file is provided
       
#             # Update the file name and file data
#             uploaded_file.file_data = file.read()

#             # Commit the session
#             scoped_session.commit()

#         # Redirect to the list of all files
#         return redirect('/login/all_files')

#     except Exception as e:
#         # Handle exceptions
#         error_message = str(e)
#         return render_template("error.html", message=error_message), 500


# @app.route('/login/delete/<int:id>')
# def delete(id):
#     token = request.cookies.get('jwt_token')
#     with app.app_context():
#         scoped_session = create_scoped_session()
#         uploaded_file = scoped_session.query(UploadedFile).get(id)
    
#     if not token:
#         return render_template('index.html')
    

#     try:
#         with app.app_context():
#             scoped_session = create_scoped_session()
#         # Delete the uploaded file from the database
#             scoped_session.delete(uploaded_file)
#             files = scoped_session.query(UploadedFile).filter(UploadedFile.keyword.like(f'{SEARCH}%')).all()
#             files_data = [{'id': file.id, 'keyword': file.keyword,'file_name': file.file_name,'user':file.user, 'location':file.location ,'contact'
#                         :file.contact , 'email' :file.email} for file in files]
#             scoped_session.commit()
#             scoped_session.close()
#     except Exception as e:
#         print("Error deleting file: " + str(e))
#         return render_template("homepage.html")


#     if not uploaded_file:
#         return render_template("search_result.html", search_results=files_data, 
#                        keyword=request.args.get('keyword'), 
#                        user=request.args.get('user'), 
#                        email=request.args.get('email'), 
#                        contact=request.args.get('contact'), 
#                        location=request.args.get('location'),
#                        selectExperiance=request.args.get('selectExperiance'), 
#                        selectCTC=request.args.get('selectCTC'))


#     #return jsonify(message= 'Uploaded file deleted successfully.', serach_result= files_data), 200
#     #return render_template("search_result.html",  search_results =files_data)
#     #redirect to the same page
#     return render_template("search_result.html", search_results=files_data, 
#                        keyword=request.args.get('keyword'), 
#                        user=request.args.get('user'), 
#                        email=request.args.get('email'), 
#                        contact=request.args.get('contact'), 
#                        location=request.args.get('location'),
#                        selectExperiance=request.args.get('selectExperiance'), 
#                        selectCTC=request.args.get('selectCTC'))
    


@app.route('/login/delete/<int:id>')
def delete(id):
    token = request.cookies.get('jwt_token')
    
    # if not token:
    #     return render_template('index.html')

    try:
        # Query the database to find the uploaded file record based on the provided id
        with app.app_context():
            scoped_session = create_scoped_session()
            uploaded_file = scoped_session.query(UploadedFile).get(id)
            scoped_session.delete(uploaded_file)
            scoped_session.commit()
            files = scoped_session.query(UploadedFile).filter(UploadedFile.keyword.like(f'{SEARCH}%')).all()
            files_data = [{'id': file.id, 'keyword': file.keyword,'file_name': file.file_name,'user':file.user, 'location':file.location ,'contact'
                        :file.contact , 'email' :file.email} for file in files]
            scoped_session.close()
            if not files_data :
                return render_template('homepage.html')
            return render_template("search_result.html",  search_results =files_data)

           
        
            # Check if the file exists
        
    except Exception as e:
        print("Error deleting file: " + str(e))
        return render_template("error.html", message="Error deleting file"), 500

    