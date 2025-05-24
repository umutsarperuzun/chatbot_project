from flask import Blueprint

# Create Blueprint for OneDrive
onedrive_bp = Blueprint('onedrive_bp', __name__, url_prefix='/onedrive')

# Import routes to register them with the Blueprint
from . import routes
