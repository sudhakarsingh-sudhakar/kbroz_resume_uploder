from app import *
from flask import Flask

# Create the Flask app
app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug=True,port=8000)
