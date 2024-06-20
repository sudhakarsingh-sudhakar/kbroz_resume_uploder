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

 

    

    
    

@app.route('/login', methods=['POST', 'GET'])
def login_route():
    try:
        token = request.cookies.get('jwt_token')
        email = request.form.get('email')
        password = request.form.get('password')

        if request.method == "GET" and token:
            return render_template("homepage_search.html")

        if not email or not password:
            return render_template("index.html")
        with app.app_context():
            scoped_session = create_scoped_session()

            user = scoped_session.query(User).filter_by(email=email, password=password).first()
            scoped_session.close()

            if user:
                token = generate_token(email)
                response = make_response(jsonify({'status': True, 'message': 'Login successful', 'token': token , 'email': email}), 200)
                response.set_cookie('jwt_token', token, httponly=True, secure=False)    # Set secure=False to exclude the Secure attribute
                return render_template('homepage_search.html', token=token)
            else:
                return render_template('index.html', message='Invalid email or password'), 401

    except Exception as e:
        # Log the exception or handle it appropriately
        return render_template('error.html', message='An error occurred. Please try again later.'), 500


@app.route('/')
def index():
    return render_template('index.html')



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
            return render_template("homepage_search.html")

        with app.app_context():
            # Create a scoped session
            scoped_session = create_scoped_session()
            # for existing user
            existing_user = scoped_session.query(UploadedFile).filter((UploadedFile.contact == contact)
                             | (UploadedFile.email == email )).first()
            if existing_user:
                return render_template ("homepage_search.html", message = " Email or Contact number already exist")
            # Create the UploadedFile object and add it to the session
            uploaded_file = UploadedFile(keyword=keyword, user=user, file_name=file_name,
                                         salary=salary, experience=experience, location=location,
                                         email=email, contact=contact, file_data=file.read())
            scoped_session.add(uploaded_file)
            
            # Commit the changes to the database
            scoped_session.commit()
            scoped_session.close()


        # Redirect to the login route with a success message
        return render_template('homepage_search.html', message='Your details were successfully received.')

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




# #API route for listing files based on search criteria
# @app.route('/login/all_files', methods=['GET'])
# def list_files():
#     global SEARCH
#     try:
#         # Get query parameters from request
#         partial_keyword = request.args.get('keyword')
#         partial_user = request.args.get('user')
#         partial_email = request.args.get('email')
#         partial_contact = request.args.get('contact')
#         partial_location = request.args.get('location')
#         partial_experience = request.args.get('selectExperiance')
#         partial_salary = request.args.get('selectCTC')

#         print(f"Received query parameters: Keyword: {partial_keyword}, User: {partial_user}, Email: {partial_email}, Contact: {partial_contact}, Location: {partial_location}, Experience: {partial_experience}, Salary: {partial_salary}")

#         # Check if JWT token is present
#         token = request.cookies.get('jwt_token')
#         if not token:
#             return render_template('index.html')

#         if partial_keyword and partial_experience and partial_salary:
#           SEARCH = partial_keyword
#           with app.app_context():
#             # Create a scoped session
#             scoped_session = create_scoped_session()
#             files = (scoped_session.query(UploadedFile)
#                     .filter(and_(
#                         UploadedFile.keyword.like(f'{partial_keyword}%'),
#                         UploadedFile.experience == partial_experience,
#                         UploadedFile.salary == partial_salary
#                     ))
#                     .all())
#             files_data = [{'id': file.id, 'keyword': file.keyword, 'file_name': file.file_name,
#                         'user': file.user, 'location': file.location, 'salary': file.salary,
#                         'experience': file.experience, 'email': file.email, 'contact': file.contact}
#                         for file in files]
            

#         # Check if any files matching the search criteria were found
#             if not files_data:
#                 return render_template("homepage.html", message="No files found matching the search criteria.")
#         return render_template("search_result.html" ,search_results =files_data)


#     except SQLAlchemyError as e:
#         # Handle SQLAlchemy errors
#         error_message = str(e)
#         return render_template("error.html", message=error_message), 500

#     except Exception as e:
#         # Handle other exceptions
#         error_message = str(e)
#         return render_template("error.html", message=error_message), 500

@app.route('/login/all_files', methods=['GET'])
def list_files():
    global SEARCH
    # Define experience mapping
    experience_dict = {
        "exp1": "0",
        "exp2": "1-3",
        "exp3": "4-6",
        "exp4": "7-10",
        "exp5": "11-15",
        "exp6": "16-20",
        "exp7": "20"
    }
    ctc_dict = {
    "CTC1": "0-3",
    "CTC2": "4-8",
    "CTC3": "9-12",
    "CTC4": "13-16",
    "CTC5": "17-20",
    "CTC6": "21-25",
    "CTC7": "26+"
    }
    ctc_keys = list(ctc_dict.keys())

    # Extract keys from the dictionary
    experience_keys = list(experience_dict.keys())

    try:
        # Get query parameters
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
        if not token:
            return render_template('index.html')
        
        # Check if no search criteria are provided
        if not any([partial_keyword, partial_user, partial_email, partial_contact, partial_location, partial_experience, partial_salary]):
            return render_template('homepage_search.html', message="Please enter at least one search criteria.")


        # Create a list to hold filters
        filters = []
        if partial_keyword:
            filters.append(UploadedFile.keyword.like(f'%{partial_keyword}%'))
            print(f"{filters} partial_keyword")
        if partial_user:
            filters.append(UploadedFile.user.like(f'%{partial_user}%'))
            print(f"{filters} partial_user")
        if partial_email:
            filters.append(UploadedFile.email.like(f'%{partial_email}%'))
            print(f"{filters} partial_email")
        if partial_contact:
            filters.append(UploadedFile.contact.like(f'%{partial_contact}%'))
            print(f"{filters} partial_contact")
        if partial_location:
            filters.append(UploadedFile.location.like(f'%{partial_location}%'))
            print(f"{filters} partial_location")
        # if partial_experience:
        #     filters.append(UploadedFile.experience == partial_experience)
        #     print(f"{filters} partial_experience")
        # if partial_salary:
        #     filters.append(UploadedFile.salary == partial_salary)
        #     print(f"{filters} partial_salary")
        print(f"{filters} filters")
        if partial_experience:
            user_experience = int(partial_experience.strip('<>='))
            operator = partial_experience[0]  # '<', '>', or '='
            experience_keys_to_filter = []

            if operator == '<':
                # Include ranges where the upper bound is less than or equal to user_experience
                for key in experience_keys:
                    exp_range = experience_dict[key]
                    if '-' in exp_range:
                        lower_bound, upper_bound = map(int, exp_range.split('-'))
                        if upper_bound < user_experience or (lower_bound <= user_experience <= upper_bound):
                            experience_keys_to_filter.append(key)
                    elif exp_range == '0' and user_experience > 0:
                        experience_keys_to_filter.append(key)
                    elif exp_range.endswith('+') and user_experience >= int(exp_range[:-1].strip()):
                        experience_keys_to_filter.append(key)
                print(f"Keys for experience less than or equal to {user_experience}: {experience_keys_to_filter}")

            elif operator == '>':
                # Include ranges where the lower bound is greater than or equal to user_experience
                for key in experience_keys:
                    exp_range = experience_dict[key]
                    if '-' in exp_range:
                        lower_bound, upper_bound = map(int, exp_range.split('-'))
                        if lower_bound > user_experience or (lower_bound <= user_experience <= upper_bound):
                            experience_keys_to_filter.append(key)
                    elif exp_range.endswith('+'):
                        experience_keys_to_filter.append(key)
                    elif int(exp_range) > user_experience:
                        experience_keys_to_filter.append(key)
                print(f"Keys for experience greater than or equal to {user_experience}: {experience_keys_to_filter}")

            elif operator == '=':
                # Include ranges that cover exactly user_experience
                for key in experience_keys:
                    exp_range = experience_dict[key]
                    if '-' in exp_range:
                        lower_bound, upper_bound = map(int, exp_range.split('-'))
                        if lower_bound <= user_experience <= upper_bound:
                            experience_keys_to_filter.append(key)
                    elif exp_range.endswith('+') and user_experience >= int(exp_range[:-1].strip()):
                        experience_keys_to_filter.append(key)
                    elif exp_range == str(user_experience):
                        experience_keys_to_filter.append(key)
                print(f"Keys for exact experience {user_experience}: {experience_keys_to_filter}")

            # Convert experience keys to actual experience ranges or values

        #print(f"Flattened experience values: {flattened_experience_values}")

        # Use the flattened experience values in the SQLAlchemy filter
            filters.append(UploadedFile.experience.in_(experience_keys_to_filter))
        # Handle CTC (Salary) filter
        if partial_salary:
            user_ctc = int(partial_salary.strip('<>='))
            operator = partial_salary[0]  # Get '<', '>', or '='
            ctc_keys_to_filter = []
            if operator == '<':
                # Include ranges where the upper bound is less than or equal to user_experience
                for key in ctc_keys:
                    exp_range = ctc_dict[key]
                    if '-' in exp_range:
                        lower_bound, upper_bound = map(int, exp_range.split('-'))
                        if upper_bound < user_ctc or (lower_bound <= user_ctc <= upper_bound):
                            ctc_keys_to_filter.append(key)
                    elif exp_range == '0' and user_ctc > 0:
                        ctc_keys_to_filter.append(key)
                    elif exp_range.endswith('+') and user_ctc >= int(exp_range[:-1].strip()):
                        ctc_keys_to_filter.append(key)
                print(f"Keys for ctc less than or equal to {user_ctc}: {ctc_keys_to_filter}")
            elif operator == '>':
                # Include ranges where the lower bound is greater than or equal to user_experience
                for key in ctc_keys:
                    exp_range = ctc_dict[key]
                    if '-' in exp_range:
                        lower_bound, upper_bound = map(int, exp_range.split('-'))
                        if lower_bound > user_ctc or (lower_bound <= user_ctc <= upper_bound):
                            ctc_keys_to_filter.append(key)
                    elif exp_range.endswith('+'):
                        ctc_keys_to_filter.append(key)
                    elif int(exp_range) > user_ctc:
                        ctc_keys_to_filter.append(key)
                print(f"Keys for ctc greater than or equal to {user_ctc}: {ctc_keys_to_filter}")
            elif operator == '=':
                # Include ranges that cover exactly user_experience
                for key in ctc_keys:
                    exp_range = ctc_dict[key]
                    if '-' in exp_range:
                        lower_bound, upper_bound = map(int, exp_range.split('-'))
                        if lower_bound <= user_ctc <= upper_bound:
                            ctc_keys_to_filter.append(key)
                    elif exp_range.endswith('+') and user_ctc >= int(exp_range[:-1].strip()):
                        ctc_keys_to_filter.append(key)
                    elif exp_range == str(user_ctc):
                        ctc_keys_to_filter.append(key)
                print(f"Keys for exact experience {user_ctc}: {ctc_keys_to_filter}")

            filters.append(UploadedFile.salary.in_(ctc_keys_to_filter))


            
              
            

        SEARCH = filters
        print(f"{filters}:.....")

        # Apply filters only if they exist
        query = UploadedFile.query

        if filters:
            query = query.filter(*filters)
            print(f"{query} querry")

        files = query.all()
        #SEARCH = files
        
        print(f"{files} files ..... {SEARCH}")

        # Convert result to list of dictionaries
        files_data = [
            {
                'id': file.id,
                'keyword': file.keyword,
                'file_name': file.file_name,
                'user': file.user,
                'location': file.location,
                'salary': file.salary,
                'experience': file.experience,
                'email': file.email,
                'contact': file.contact
            } for file in files
        ]
        print(f"{files_data} files data")

        # Check if any files were found
        if not files_data:
            return render_template("homepage_search.html", message=" No files found matching the search criteria.")

        return render_template("search_result.html", search_results=files_data)

    except SQLAlchemyError as e:
        error_message = str(e)
        return render_template("error.html", message=error_message), 500

    except Exception as e:
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
        #files = UploadedFile.query.filter(UploadedFile.keyword.like(f'{SEARCH}%')).all()
        files = UploadedFile.query.filter(*SEARCH).all()
        #files = SEARCH
        print(f"akay {files}")
        files_data = [{'id': file.id, 'keyword': file.keyword,'file_name': file.file_name,'user':file.user, 'location':file.location ,'contact'
                   :file.contact , 'email' :file.email,'file_data': uploaded_file.file_data} for file in files]
        db.session.commit()
        return render_template("search_result.html",  search_results =files_data)


    #files = UploadedFile.query.filter(UploadedFile.keyword.like(f'{SEARCH}%')).all()
    #files = SEARCH
    files = UploadedFile.query.filter(*SEARCH).all()
    print(f"niraj{files}")
    files_data = [{'id': file.id, 'keyword': file.keyword,'file_name': file.file_name,'user':file.user, 'location':file.location ,'contact'
                   :file.contact , 'email' :file.email} for file in files]

    db.session.commit()

    return render_template("search_result.html",  search_results =files_data)


# # API route for updating a file


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
            #files = scoped_session.query(UploadedFile).filter(UploadedFile.keyword.like(f'{SEARCH}%')).all()
            files = scoped_session.query(UploadedFile).filter(*SEARCH).all()
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

    