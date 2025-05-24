from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from forms import ResponseForm
from models import db, Category, Variation, Response, Type
import logging

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)

# Category or Type get/creating function
def get_or_create_category(name, type_id):
    category = Category.query.filter_by(name=name).first()
    if not category:
        type_instance = Type.query.get(type_id)
        if not type_instance:
            return None, "Invalid type selected."
        category = Category(name=name, type_id=type_instance.id)
        db.session.add(category)
        db.session.commit()
    return category, None

# Admin panel route
@admin_bp.route('/', methods=['GET', 'POST'])
def admin():
    form = ResponseForm()
    responses = Response.query.all()
    if form.validate_on_submit():
        try:
            # Add new category or find existing category
            category, error = get_or_create_category(form.category.data, form.type.data)
            if error:
                flash(error, "danger")
                return redirect(url_for('admin_bp.admin'))
            # If the category exists or is newly added, add variation and answer
            for var_text in form.variation.data.split(','):
                var_text = var_text.strip()
                if var_text:
                    existing_variation = Variation.query.filter_by(text=var_text, category=category).first()
                    if not existing_variation:
                        new_variation = Variation(text=var_text, category=category)
                        db.session.add(new_variation)
            for res_text in form.response.data.split(','):
                res_text = res_text.strip()
                if res_text:
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
        return redirect(url_for('admin_bp.admin'))
    return render_template('admin.html', form=form, responses=responses)

# Update Route
@admin_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def update_response(id):
    response = Response.query.get_or_404(id)
    form = ResponseForm(obj=response)
    form.category.data = response.category.name
    form.variation.data = ', '.join([v.text for v in response.category.variations])
    form.response.data = response.text
    if form.validate_on_submit():
        try:
            response.text = form.response.data.strip()
            category, error = get_or_create_category(form.category.data, form.type.data)
            if error:
                flash(error, "danger")
                return redirect(url_for('admin_bp.admin'))
            response.category = category
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
        return redirect(url_for('admin_bp.admin'))
    return render_template('update_response.html', form=form, response=response)

# Variation adding route
@admin_bp.route('/add_variation/<int:id>', methods=['POST'])
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
    return redirect(url_for('admin_bp.update_response', id=id))

# Add answer route
@admin_bp.route('/add_response/<int:id>', methods=['POST'])
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
    return redirect(url_for('admin_bp.update_response', id=id))

# Variation deletion route
@admin_bp.route('/delete_variation/<int:id>', methods=['POST'])
def delete_variation(id):
    variation = Variation.query.get_or_404(id)
    category_id = variation.category.id
    try:
        db.session.delete(variation)
        db.session.commit()
        flash("Variation deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting variation: {e}")
        flash("An error occurred while deleting the variation.", "danger")
    return redirect(url_for('admin_bp.update_response', id=category_id))

# Delete response route
@admin_bp.route('/delete_response/<int:id>', methods=['POST'])
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
    return redirect(url_for('admin_bp.admin'))

# Delete category route
@admin_bp.route('/delete_category/<int:id>', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    try:
        Variation.query.filter_by(category_id=category.id).delete()
        Response.query.filter_by(category_id=category.id).delete()
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting category: {e}")
        flash("An error occurred while deleting the category.", "danger")

    return redirect(url_for('admin_bp.admin'))
