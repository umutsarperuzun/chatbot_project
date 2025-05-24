from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime



db = SQLAlchemy()


# Category model
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    type_id = db.Column(db.Integer, db.ForeignKey('types.id'), nullable=True)
    variations = db.relationship('Variation', backref='category', lazy='subquery', cascade="all, delete-orphan")
    responses = db.relationship('Response', backref='category', lazy='subquery', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category {self.name}>"

# Types Model
class Type(db.Model):
    __tablename__ = 'types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    categories = db.relationship('Category', backref='type', lazy='subquery')

    def __repr__(self):
        return f"<Type {self.name}>"

# Variation Model
class Variation(db.Model):
    __tablename__ = 'variations'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    def __repr__(self):
        return f"<Variation {self.text}>"

# Response Model
class Response(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    def __repr__(self):
        return f"<Response {self.text}>"

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)  # password yerine department eklendi
    chat_history = db.Column(db.Text, nullable=True)
    onedrive_access_token = db.Column(db.Text, nullable=True)  
    onedrive_refresh_token = db.Column(db.Text, nullable=True)  
    state = db.Column(db.String(32), nullable=True)  # Mevcut state alanı olduğu gibi bırakıldı

    def __repr__(self):
        return f"<User {self.username} - Department {self.department}>"


class MaintenanceReport(db.Model):
    __tablename__ = 'maintenance_reports'
    id = db.Column(db.Integer, primary_key=True)
    issue_title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    urgency = db.Column(db.String(10), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    type_of_maintenance = db.Column(db.String(50), nullable=True)
    date_submitted = db.Column(db.DateTime, default=func.now())  # Bu satırı güncelledik!

    def __repr__(self):
        return f"<MaintenanceReport {self.issue_title} - {self.urgency}>"


class VehicleInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    last_maintenance_date = db.Column(db.Date, nullable=True)
    next_maintenance_date = db.Column(db.Date, nullable=True)
    work_type = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<VehicleInfo {self.plate_number}>'


class SentimentLog(db.Model):
    __tablename__ = 'sentiment_logs'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)  
    sentiment = db.Column(db.String(50), nullable=False)  
    confidence = db.Column(db.Float, nullable=False)  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  
