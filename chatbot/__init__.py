from flask import Blueprint

# Define the chatbot Blueprint with a URL prefix
chatbot_bp = Blueprint('chatbot_bp', __name__, url_prefix='/chatbot')

# Import the routes associated with the chatbot Blueprint
from . import routes
