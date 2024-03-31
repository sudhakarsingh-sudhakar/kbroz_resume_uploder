from flask import Flask

app = Flask(__name__)

# Import your views after initializing the Flask app to avoid circular imports
from app import views
