from flask import Blueprint, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            
            new_user = User(username=form.username.data, department=form.department.data)
            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('auth_bp.login'))  # Redirect to login page
        except Exception as e:
            db.session.rollback()  # Rollback changes in case of error
            flash(f"An error occurred during registration: {e}", "danger")
    elif form.errors:
        flash(f"Form validation errors: {form.errors}", "danger")
    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print("Login route accessed")
    if form.validate_on_submit():
        print("Form submitted with:", form.username.data, form.department.data)
        
        user = User.query.filter_by(username=form.username.data, department=form.department.data).first()
        
        if user:
            print("User found:", user.username)
            
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('chatbot_bp.index'))
        else:
            print("Invalid username or department")
            flash("Invalid username or department.", "danger")
    elif form.errors:
        print("Form errors:", form.errors)
        flash(f"Form validation errors: {form.errors}", "danger")
    return render_template('login.html', form=form)



@auth_bp.route('/logout', methods=['GET'])
def logout():
    
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        
        if user:
            
            user.chat_history = None
            user.onedrive_access_token = None
            user.onedrive_refresh_token = None
            db.session.commit()

    
    session.clear()  # Clear the session
    flash("You have been logged out and your data has been cleared.", "info")
    return redirect(url_for('auth_bp.login'))  # Redirect to login page
