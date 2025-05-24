from flask import Flask, redirect, url_for,session
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from models import db
from admin.routes import admin_bp
from chatbot.routes import chatbot_bp
from onedrive.routes import onedrive_bp
from auth.routes import auth_bp  # Import the authentication blueprint
from flask_session import Session
from datetime import timedelta



app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)
# Configuration

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True  
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24) 
app.config['SESSION_USE_SIGNER'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://chatbot_user:password@localhost/chatbot_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Session(app)

# Initialize database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')  # Chatbot routes
app.register_blueprint(onedrive_bp, url_prefix='/onedrive')  # OneDrive routes
app.register_blueprint(auth_bp, url_prefix='/auth')  # Authentication routes

# Set the default route to the login page
@app.route('/')
def home():
    return redirect(url_for('auth_bp.login'))  # Redirect to the login page

@app.route('/csrf_test')
def csrf_test():
    from flask import session
    csrf_token = session.get('_csrf_token')
    print("Session'daki CSRF Token:", csrf_token)
    return f"CSRF Token: {csrf_token}"

# Error handling
@app.errorhandler(404)
def page_not_found(error):
    return "Page not found. Please check the URL.", 404

@app.errorhandler(500)
def internal_server_error(error):
    return "An internal server error occurred. Please try again later.", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(port=5000,debug=True)
