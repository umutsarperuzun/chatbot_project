from flask_sqlalchemy import SQLAlchemy

# Veritabanı nesnesini başlat
db = SQLAlchemy()

# Kategori Modeli
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    type_id = db.Column(db.Integer, db.ForeignKey('types.id'), nullable=True)
    variations = db.relationship('Variation', backref='category', lazy='subquery', cascade="all, delete-orphan")
    responses = db.relationship('Response', backref='category', lazy='subquery', cascade="all, delete-orphan")
    
# Tip Modeli
class Type(db.Model):
    __tablename__ = 'types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    categories = db.relationship('Category', backref='type', lazy='subquery')

# Varyasyon Modeli
class Variation(db.Model):
    __tablename__ = 'variations'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

# Yanıt Modeli
class Response(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
