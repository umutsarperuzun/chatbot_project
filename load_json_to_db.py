import json
from app import db  
from models import Category, Variation, Response, Type 

def load_json_to_db(json_file_path):
    """
    Load data from a JSON file into the database.
    """
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Create or fetch a default type for categorization
    default_type = Type.query.filter_by(name="Sentiment").first()
    if not default_type:
        default_type = Type(name="Sentiment")
        db.session.add(default_type)
        db.session.commit()

    for category_name, content in data['responses'].items():
        # Add or find category
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name, type=default_type)
            db.session.add(category)
            db.session.commit()
        
        # Add variations
        for variation_text in content['variations']:
            variation = Variation.query.filter_by(text=variation_text, category_id=category.id).first()
            if not variation:
                variation = Variation(text=variation_text, category=category)
                db.session.add(variation)
        
        # Add responses
        for response_text in content['responses']:
            response = Response.query.filter_by(text=response_text, category_id=category.id).first()
            if not response:
                response = Response(text=response_text, category=category)
                db.session.add(response)

    db.session.commit()
    print("Data successfully loaded into the database!")
