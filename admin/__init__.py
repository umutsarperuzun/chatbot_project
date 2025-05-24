from flask import Blueprint

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# Import the routes to register them with the Blueprint
from . import routes
