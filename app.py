from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from forms import ResponseForm
import spacy
from fuzzywuzzy import fuzz
import random
import logging
from models import db, Category, Variation, Response, Type


#  this is my project


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://chatbot_user:password@localhost/chatbot_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

nlp = spacy.load("en_core_web_sm")
chat_history = []

# Ana sayfa rotası
@app.route('/')
def index():
    return render_template('answer.html', chat_history=chat_history)

# Veritabanından yanıtları yükleme fonksiyonu
def load_responses():
    responses = {}
    all_categories = Category.query.all()
    for category in all_categories:
        responses[category.name] = {
            "variations": [var.text for var in category.variations],
            "responses": [res.text for res in category.responses]
        }
    return responses

# En uygun yanıtı bulma fonksiyonu
def find_best_response(user_message):
    doc = nlp(user_message)
    responses = load_responses()
    
    for category, content in responses.items():
        for token in doc:
            if token.lemma_ in content["variations"]:
                return random.choice(content["responses"])

    best_match = None
    highest_ratio = 0
    for category, content in responses.items():
        for variation in content["variations"]:
            match_ratio = fuzz.ratio(user_message, variation)
            if match_ratio > highest_ratio and match_ratio > 70:
                best_match = content
                highest_ratio = match_ratio

    if best_match:
        return random.choice(best_match["responses"])

    return "I didn't understand that. Can you ask something else."

# Chatbot yanıtı döndüren /answer rotası
@app.route('/answer', methods=['POST'])
def answer():
    user_message = request.form.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    bot_response = find_best_response(user_message)
    chat_history.append({"sender": "user", "text": user_message})
    chat_history.append({"sender": "bot", "text": bot_response})
    
    return render_template('answer.html', chat_history=chat_history)

# Admin paneli rotası
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = ResponseForm()
    responses = Response.query.all()
    
    if form.validate_on_submit():
        try:
            # Yeni kategori ekle veya mevcut kategoriyi bul
            category = Category.query.filter_by(name=form.category.data).first()
            if not category:
                # Yeni kategori oluştur ve type_id'yi atayarak ekle
                type_instance = Type.query.get(form.type.data)
                if not type_instance:
                    flash("Invalid type selected.", "danger")
                    return redirect(url_for('admin'))

                category = Category(name=form.category.data, type_id=type_instance.id)
                db.session.add(category)
                db.session.commit()  # Yeni kategori oluşturulduktan sonra commit yap
                flash("New category added successfully!", "success")
            else:
                flash("Category already exists.", "warning")

            # Eğer kategori mevcutsa veya yeni eklenmişse, varyasyon ve yanıt ekle
            if category:
                # Varyasyon ekle (tekrarlayan varyasyon kontrolü)
                for var_text in form.variation.data.split(','):
                    var_text = var_text.strip()
                    existing_variation = Variation.query.filter_by(text=var_text, category=category).first()
                    if not existing_variation:
                        new_variation = Variation(text=var_text, category=category)
                        db.session.add(new_variation)

                # Yanıt ekle (tekrarlayan yanıt kontrolü)
                for res_text in form.response.data.split(','):
                    res_text = res_text.strip()
                    existing_response = Response.query.filter_by(text=res_text, category=category).first()
                    if not existing_response:
                        new_response = Response(text=res_text, category=category)
                        db.session.add(new_response)

                db.session.commit()
                flash("New response and variations added successfully!", "success")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding response: {e}")
            flash("An error occurred while adding the response.", "danger")
        return redirect(url_for('admin'))
    
    return render_template('admin.html', form=form, responses=responses)

# Güncelleme rotası
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_response(id):
    response = Response.query.get_or_404(id)
    form = ResponseForm(obj=response)
    form.category.data = response.category.name
    form.variation.data = ', '.join([v.text for v in response.category.variations])
    form.response.data = response.text

    if form.validate_on_submit():
        try:
            # Yanıtı güncelle
            response.text = form.response.data.strip()
            
            # Kategoriyi güncelle veya yeni kategori ekle
            category = Category.query.filter_by(name=form.category.data).first()
            if not category:
                type_instance = Type.query.get(form.type.data)
                if not type_instance:
                    flash("Invalid type selected.", "danger")
                    return redirect(url_for('admin'))

                category = Category(name=form.category.data, type_id=type_instance.id)
                db.session.add(category)
            response.category = category

            # Varyasyonları güncelle
            Variation.query.filter_by(category=category).delete()
            for var_text in form.variation.data.split(','):
                var_text = var_text.strip()
                if var_text:
                    new_variation = Variation(text=var_text, category=category)
                    db.session.add(new_variation)

            db.session.commit()
            flash("Response updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating response: {e}")
            flash("An error occurred while updating the response.", "danger")
        return redirect(url_for('admin'))
    
    return render_template('update_response.html', form=form, response=response)

# Varyasyon ekleme rotası
@app.route('/add_variation/<int:id>', methods=['POST'])
def add_variation(id):
    response = Response.query.get_or_404(id)
    category = response.category
    new_variation_text = request.form.get("new_variation", "").strip()

    if new_variation_text:
        existing_variation = Variation.query.filter_by(text=new_variation_text, category=category).first()
        if not existing_variation:
            new_variation = Variation(text=new_variation_text, category=category)
            db.session.add(new_variation)
            db.session.commit()
            flash("New variation added successfully!", "success")
        else:
            flash("This variation already exists.", "warning")
    else:
        flash("No variation text provided.", "error")
    
    return redirect(url_for('update_response', id=id))

# Yanıt ekleme rotası
@app.route('/add_response/<int:id>', methods=['POST'])
def add_response(id):
    response = Response.query.get_or_404(id)
    category = response.category
    new_response_text = request.form.get("new_response", "").strip()

    if new_response_text:
        try:
            existing_response = Response.query.filter_by(text=new_response_text, category=category).first()
            if not existing_response:
                new_response = Response(text=new_response_text, category=category)
                db.session.add(new_response)
                db.session.commit()
                flash("New response added successfully!", "success")
            else:
                flash("This response already exists.", "warning")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding response: {e}")
            flash("An error occurred while adding the response.", "danger")
    else:
        flash("No response text provided.", "error")
    
    return redirect(url_for('update_response', id=id))

# Varyasyon silme rotası
@app.route('/delete_variation/<int:id>', methods=['POST'])
def delete_variation(id):
    variation = Variation.query.get_or_404(id)
    category_id = variation.category.id  # Kategorinin ID'sini alın
    try:
        db.session.delete(variation)
        db.session.commit()
        flash("Variation deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting variation: {e}")
        flash("An error occurred while deleting the variation.", "danger")
    return redirect(url_for('update_response', id=category_id))

# Yanıt silme rotası
@app.route('/delete_response/<int:id>', methods=['POST'])
def delete_response(id):
    response = Response.query.get_or_404(id)
    try:
        db.session.delete(response)
        db.session.commit()
        flash("Response deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting response: {e}")
        flash("An error occurred while deleting the response.", "danger")
    return redirect(url_for('admin'))

@app.route('/delete_category/<int:id>', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    try:
        # Varyasyonları ve yanıtları sil
        Variation.query.filter_by(category_id=category.id).delete()
        Response.query.filter_by(category_id=category.id).delete()

        # Kategoriyi sil
        db.session.delete(category)
        db.session.commit()
        flash("Kategori başarıyla silindi!", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Kategori silinirken hata oluştu: {e}")
        flash("Kategori silinirken bir hata oluştu.", "danger")
    
    return redirect(url_for('admin'))

# running maingit  application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)



# $app = New-AzADApplication -DisplayName "DissertationCBP" -IdentifierUris "https://DissertationCBP"





