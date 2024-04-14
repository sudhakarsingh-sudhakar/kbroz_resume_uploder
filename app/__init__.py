from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from run import secret_key_str

app = Flask(__name__)
# app = Flask(__name__,
#         static_url_path='', 
#         static_folder='app/static',
#         template_folder='app/templates')

# Set the secret key for the Flask application
app.config['SECRET_KEY'] = secret_key_str
# # Configure MySQL connection parameters
# mysql_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'Niraj',
#     'database': 'new_etm',  # Replace 'your_database_name' with the actual database name
#     'port': 3306,  # MySQL default port is 3306
# }

# # Establish MySQL connection
# db_connection = mysql.connector.connect(**mysql_config)

# Configure MySQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Niraj@localhost:3306/new_etm'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# Import your views after initializing the Flask app to avoid circular imports
from app import views

# Import models module to ensure the models are created
from app import models
