from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from run import secret_key_str
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key_str

# # Configure MySQL database connection
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Niraj@localhost:3306/new_etm'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://u692835114_Admin:Prm_12345@srv1474.hstgr.io:3306/u692835114_pr_resumedb'

# # Initialize SQLAlchemy
db = SQLAlchemy(app)
# db = PyMongo(app)
# Define a function to create the scoped session
def create_scoped_session():
    return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db.engine))

# Bind the session to the application context
# @app.teardown_appcontext
# def remove_session(*args, **kwargs):
#     db_session.remove()

# # Import your views after initializing the Flask app to avoid circular imports
from app import views

# # Import models module to ensure the models are created
from app import models
