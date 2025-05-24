from flask import Blueprint, request, render_template, session, redirect, url_for, flash, jsonify, Response
import spacy
import random
from models import db, User, Category,MaintenanceReport,VehicleInfo,SentimentLog
from onedrive.routes import perform_onedrive_action  # Import OneDrive handler
from onedrive.routes import download_file_by_id
from onedrive.routes import share_file_by_id
from onedrive.routes import search_files
from forms import MessageForm,MaintenanceReportForm,VehicleCreateForm,VehicleUpdateForm
from fuzzywuzzy import fuzz
import requests
from microsoftgraph.client import Client
from flask_wtf import csrf
from utils.sentiment import analyze_sentiment_with_threshold
from datetime import datetime, timedelta
from sarper_secrets import get_secrets


graph_client = get_secrets()


# Define the blueprint
chatbot_bp = Blueprint('chatbot_bp', __name__)
# Load SpaCy model
nlp = spacy.load("en_core_web_sm")


# Load responses from the database
def load_responses():
    """Fetch categories, variations, and responses from the database."""
    responses = {}
    try:
        all_categories = Category.query.all()
        for category in all_categories:
            responses[category.name] = {
                "variations": [var.text.strip().lower() for var in category.variations],
                "responses": [res.text.strip() for res in category.responses]
            }
    except Exception as e:
        print(f"Error loading responses: {e}")
    return responses

def find_best_response(user_message):
    """Process user input and return the best response or handle OneDrive actions."""
    responses = load_responses()
    user_message = user_message.strip().lower()

    # Sentiment Analysis Integration
    sentiment, confidence = analyze_sentiment_with_threshold(user_message)
    if sentiment == "NEGATIVE":
        sentiment_response = "I'm sorry to hear that. Can I assist you with something specific?"
    elif sentiment == "POSITIVE":
        sentiment_response = "Thank you for the positive feedback! Let me know if there's anything else I can do."
    else:  # NEUTRAL
        sentiment_response = None  # No specific response for neutral messages

    log = SentimentLog(
    message=user_message,
    sentiment=sentiment,
    confidence=confidence,
    timestamp=datetime.utcnow() + timedelta(seconds=0)  
    )
    db.session.add(log)
    db.session.commit()

    from models import Variation, Response  
    from sqlalchemy.sql import func  
    variation = Variation.query.filter(Variation.text.ilike(f"%{user_message}%")).first()
    if variation:
        
        response = Response.query.filter_by(category_id=variation.category_id).order_by(func.random()).first()
        if response:
            return {"response": response.text, "search_mode": False}

    # Vehicle Information Viewing
    if "show vehicle" in user_message or "view vehicle" in user_message:
        plate_number = user_message.split()[-1]  # Assume plate number is the last word
        vehicle = VehicleInfo.query.filter_by(plate_number=plate_number.upper()).first()
        if not vehicle:
            return {"response": f"No vehicle found with plate number: {plate_number.upper()}", "search_mode": False}
        else:
            response = (
                f"Vehicle Info:\n"
                f"- Plate: {vehicle.plate_number}\n"
                f"- Type: {vehicle.vehicle_type}\n"
                f"- Location: {vehicle.location or 'Unknown'}\n"
                f"- Last Maintenance: {vehicle.last_maintenance_date or 'Unknown'}\n"
                f"- Next Maintenance: {vehicle.next_maintenance_date or 'Unknown'}\n"
                f"- Work Type: {vehicle.work_type or 'Unknown'}"
            )
            return {"response": response, "search_mode": False}

    # Vehicle Information Creation
    if "add vehicle" in user_message or "create vehicle" in user_message:
        return {
            "response": "Please fill out the vehicle information form below to add a new vehicle.",
            "show_vehicle_form": True  # Trigger vehicle creation form
        }

    # Vehicle Information Update
    if "update vehicle" in user_message:
        plate_number = user_message.split()[-1]  # Assume plate number is the last word
        vehicle = VehicleInfo.query.filter_by(plate_number=plate_number.upper()).first()
        if not vehicle:
            return {"response": f"No vehicle found with plate number: {plate_number.upper()} for update.", "search_mode": False}
        else:
            return {
                "response": f"Please update the information for vehicle with plate: {plate_number.upper()} below.",
                "show_update_form": True,
                "vehicle_id": vehicle.id
            }

    # Maintenance Report Viewing
    if any(phrase in user_message for phrase in ["view maintenance reports", "show maintenance reports", "list reports", "show me reports"]):
        return {
            "response": "Fetching maintenance reports...",
            "show_reports": True  # Trigger maintenance report viewing
        }

    # Maintenance Report Creation
    if any(phrase in user_message for phrase in ["create maintenance report", "new maintenance report", "add maintenance report", "create maintenance request"]):
        return {
            "response": "Please fill out the maintenance report form below:",
            "show_maintenance_form": True  # Trigger maintenance report form display
        }

    # OneDrive Actions
    if any(action in user_message for action in ["upload", "download", "search", "share"]):
        if 'user_id' not in session:
            return {"response": "Please log in to access OneDrive features.", "search_mode": False}
        user = User.query.get(session['user_id'])
        if not user or not user.onedrive_access_token:
            return {
                "response": f"Please <a href='{url_for('onedrive_bp.login')}'>log in to OneDrive</a> to connect your account.",
                "search_mode": False
            }
        else:
            action = next((word for word in ["upload", "download", "search", "share"] if word in user_message), None)
            if action in ["search", "download", "share"]:
                return {"response": "", "search_mode": True}
            return {"response": perform_onedrive_action(action, user_message), "search_mode": False}

    # General NLP and Fuzzy Matching
    best_match = None
    best_score = 0
    for category, content in responses.items():
        for variation in content["variations"]:
            similarity_score = fuzz.ratio(variation, user_message)
            if similarity_score > 70 and similarity_score > best_score:
                best_match = random.choice(content["responses"])
                best_score = similarity_score
    if best_match:
        return {"response": best_match, "search_mode": False}

    # If no predefined response is found, analyze sentiment
    if sentiment_response:
        return {"response": sentiment_response, "search_mode": False}

    # Default response
    return {"response": "I didn't understand that. Can you try rephrasing or asking something else?", "search_mode": False}


@chatbot_bp.route('/')
def index():
    if 'user_id' not in session:
        flash("Please log in to access the chatbot.", "warning")
        return redirect(url_for('auth_bp.login'))

    # Retrieve user and chat history
    user = User.query.get(session['user_id'])
    chat_history = eval(user.chat_history) if user.chat_history else []  # Convert string to list
    
    session['chat_history'] = chat_history

    # Initialize forms
    form = MessageForm()  # General message form
    maintenance_form = MaintenanceReportForm()  # Maintenance report form
    vehicle_form = VehicleCreateForm()  # Vehicle creation form
    update_vehicle_form = VehicleUpdateForm()  # Vehicle update form

    return render_template('chatbot.html',chat_history=chat_history,form=form,maintenance_form=maintenance_form,vehicle_form=vehicle_form,
        update_vehicle_form=update_vehicle_form,  
        show_vehicle_form=False,  
        show_update_vehicle_form=False  
    )

@chatbot_bp.route('/chatbot', methods=['POST', 'GET'])
def chatbot():
    if 'user_id' not in session:
        return jsonify({"error": "You need to log in to use the chatbot."}), 401
    user = User.query.get(session['user_id'])
    form = MessageForm()
    maintenance_form = MaintenanceReportForm()  # Initialize maintenance form
    vehicle_form = VehicleCreateForm()  # Initialize vehicle creation form
    update_vehicle_form = VehicleUpdateForm()  # Initialize vehicle update form
    show_search_form = False  # Control for search form visibility
    show_maintenance_form = False  # Control for maintenance form visibility
    show_vehicle_form = False  # Control for vehicle creation form visibility
    show_update_vehicle_form = False  # Control for vehicle update form visibility
    vehicle_id = None  # Initialize vehicle_id to avoid UnboundLocalError
    if form.validate_on_submit():
        user_message = form.message.data
        words = ["download","search","share"]  # Handle search trigger
        if user_message.strip().lower() in words:
            if not user.onedrive_access_token:  # If OneDrive is not connected
                bot_response = f"Please <a href='{url_for('onedrive_bp.login')}'>log in to OneDrive</a> to connect your account."
            else:  # If OneDrive is connected, show search form
                bot_response = "Please enter a query to search for files:"
                show_search_form = True
        # Handle search query submission
        elif 'query' in request.form:
            query = request.form['query']
            search_results = search_files(query)
            if isinstance(search_results, str):  # Return error message
                bot_response = search_results
            else:  # Successful search, return results
                bot_response = f"Found files: {', '.join(file['name'] for file in search_results)}"
        else:
            response_data = find_best_response(user_message)
            bot_response = response_data["response"]
            show_maintenance_form = response_data.get("show_maintenance_form", False) # Show maintenance form if triggered
            show_vehicle_form = response_data.get("show_vehicle_form", False) # Show vehicle creation form if triggered
            if response_data.get("show_update_form", False): # Show vehicle update form if triggered
                show_update_vehicle_form = True
                vehicle_id = response_data.get("vehicle_id")  # Get vehicle_id from the response
                if vehicle_id:
                    vehicle = VehicleInfo.query.get(vehicle_id)
                    if vehicle:
                        update_vehicle_form.location.data = vehicle.location
                        update_vehicle_form.last_maintenance_date.data = vehicle.last_maintenance_date
                        update_vehicle_form.next_maintenance_date.data = vehicle.next_maintenance_date
                        update_vehicle_form.work_type.data = vehicle.work_type
            if response_data.get("show_reports", False):  # Handle maintenance report viewing
                reports = MaintenanceReport.query.order_by(MaintenanceReport.date_submitted.desc()).limit(5).all()
                if not reports:
                    bot_response = "No maintenance reports found."
                else:
                    bot_response = "Here are the latest maintenance reports:\n"
                    for report in reports:
                        formatted_date = report.date_submitted.strftime('%Y-%m-%d') if report.date_submitted else "Unknown Date"
                        bot_response += f"- {report.issue_title} ({report.urgency}) - {formatted_date}\n"
        # Update chat history
        chat_history = eval(user.chat_history) if user.chat_history else []
        chat_entry_user = {"sender": "user", "text": user_message}
        chat_entry_bot = {"sender": "bot", "text": bot_response}
        chat_history.append(chat_entry_user)
        chat_history.append(chat_entry_bot)
        # Save updated history
        user.chat_history = str(chat_history)
        db.session.commit()
        return render_template('chatbot.html',chat_history=chat_history,form=form,maintenance_form=maintenance_form,vehicle_form=vehicle_form,update_vehicle_form=update_vehicle_form,
            show_search_form=show_search_form,show_maintenance_form=show_maintenance_form,show_vehicle_form=show_vehicle_form,show_update_vehicle_form=show_update_vehicle_form,vehicle_id=vehicle_id  # Pass vehicle_id to template
        )
    return render_template('chatbot.html',chat_history=session.get('chat_history', []),form=form,maintenance_form=maintenance_form,vehicle_form=vehicle_form,update_vehicle_form=update_vehicle_form,
        show_search_form=False,show_maintenance_form=False,show_vehicle_form=False,show_update_vehicle_form=False,vehicle_id=None  # Pass None as default for vehicle_id
    )


@chatbot_bp.route('/submit_maintenance_report', methods=['POST'])
def submit_maintenance_report():
    """Handles the maintenance report form and displays success message in chat."""
    form = MaintenanceReportForm()
    if form.validate_on_submit():
        new_report = MaintenanceReport(
            issue_title=form.issue_title.data,
            description=form.description.data,
            urgency=form.urgency.data,
            department=form.department.data,
            type_of_maintenance=form.type_of_maintenance.data
        )
        try:
            db.session.add(new_report)
            db.session.commit()
            # Add success message to chat history
            success_message = "Your maintenance report has been successfully submitted. Thank you!"
            chat_history = session.get('chat_history', [])
            chat_history.append({"sender": "bot", "text": success_message})
            session['chat_history'] = chat_history
        except Exception as e:
            db.session.rollback()
            chat_history = session.get('chat_history', [])
            chat_history.append({"sender": "bot", "text": "An error occurred. Please try again."})
            session['chat_history'] = chat_history
        return render_template(
            'chatbot.html',
            chat_history=session['chat_history'],
            form=MessageForm(),
            maintenance_form=MaintenanceReportForm()
        )
    # No action is taken if form validation fails
    return jsonify({"message": "Form validation failed. Please check your input."})

@chatbot_bp.route('/view_maintenance_reports', methods=['GET'])
def view_maintenance_reports():
    """Fetches a brief list of maintenance reports and displays them in the chat."""
    try:
        reports = MaintenanceReport.query.order_by(MaintenanceReport.date_submitted.desc()).limit(5).all()
        
        if not reports:
            message = "No maintenance reports found."
        else:
            message = "Here are the latest maintenance reports:\n"
            for report in reports:
                date = report.date_submitted.strftime('%Y-%m-%d') if report.date_submitted else "Unknown Date"
                message += f"- {report.issue_title} ({report.urgency}) - {date}\n"

        # Add message to chat history
        chat_history = session.get('chat_history', [])
        chat_history.append({"sender": "bot", "text": message})
        session['chat_history'] = chat_history

        return render_template(
            'chatbot.html',
            chat_history=chat_history,
            form=MessageForm(),
            maintenance_form=MaintenanceReportForm()
        )

    except Exception as e:
        print(f"Error fetching maintenance reports: {e}")
        flash("An error occurred while fetching maintenance reports. Please try again later.", "danger")
        return redirect(url_for('chatbot_bp.chatbot'))

@chatbot_bp.route('/create_vehicle', methods=['POST'])
def create_vehicle():
    
    from forms import VehicleCreateForm
    form = VehicleCreateForm()
    if form.validate_on_submit():
        
        new_vehicle = VehicleInfo(
            plate_number=form.plate_number.data,
            vehicle_type=form.vehicle_type.data,
            location=form.location.data,
            last_maintenance_date=form.last_maintenance_date.data,
            next_maintenance_date=form.next_maintenance_date.data,
            work_type=form.work_type.data
        )
        
        try:
            
            print(session['chat_history'])
            print(type(session['chat_history']))
            response={'sender': 'bot', 'text': f'New Vehicle Added.Plate number is: {new_vehicle.plate_number}'}
            session['chat_history'].append(response)
            print(session['chat_history'])
            db.session.add(new_vehicle)
            user = User.query.get(session['user_id'])
            user.chat_history = str(session['chat_history'])
            db.session.commit()                  
        except Exception as e:
            db.session.rollback()
            print(e)
            return redirect(url_for('chatbot_bp.index'))
      
    return redirect(url_for('chatbot_bp.index'))

@chatbot_bp.route('/update_vehicle/<vehicle_id>', methods=['POST'])
def update_vehicle(vehicle_id):
    from forms import VehicleUpdateForm
    form = VehicleUpdateForm()
    vehicle = VehicleInfo.query.get(vehicle_id)
    if not vehicle:
        flash("Vehicle not found.", "danger")
        return redirect(url_for('chatbot_bp.index'))
    if form.validate_on_submit():
        vehicle.location = form.location.data
        vehicle.last_maintenance_date = form.last_maintenance_date.data
        vehicle.next_maintenance_date = form.next_maintenance_date.data
        vehicle.work_type = form.work_type.data
        try:
            print(session['chat_history'])
            print(type(session['chat_history']))
            response={'sender': 'bot', 'text': f'Vehicle Updateded plate number: {vehicle.plate_number}'}
            session['chat_history'].append(response)
            print(session['chat_history'])
            db.session.add(vehicle)
            user = User.query.get(session['user_id'])
            user.chat_history = str(session['chat_history'])
            db.session.commit()  
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
    return redirect(url_for('chatbot_bp.index'))

@chatbot_bp.route('/view_vehicle/<plate_number>', methods=['GET'])
def view_vehicle(plate_number):
    vehicle = VehicleInfo.query.filter_by(plate_number=plate_number).first()
    if not vehicle:
        response = f"No vehicle found with plate number: {plate_number}."
    else:
        response = (
            f"Vehicle Info:\n"
            f"- Plate: {vehicle.plate_number}\n"
            f"- Type: {vehicle.vehicle_type}\n"
            f"- Location: {vehicle.location}\n"
            f"- Last Maintenance: {vehicle.last_maintenance_date}\n"
            f"- Next Maintenance: {vehicle.next_maintenance_date}\n"
            f"- Work Type: {vehicle.work_type}"
        )
    # Add response to chat history
    chat_history = session.get('chat_history', [])
    chat_history.append({"sender": "bot", "text": response})
    session['chat_history'] = chat_history
    return render_template('chatbot.html', chat_history=chat_history, form=MessageForm())
   
    
@chatbot_bp.route('/uploadd', methods=['POST'])
def upload_file():
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash("You need to log in to access this feature.", "danger")
        return redirect(url_for('auth_bp.login'))

    user = User.query.get(session['user_id'])
    if not user.onedrive_access_token:
        flash("Please connect to OneDrive first.", "danger")
        return redirect(url_for('onedrive_bp.login'))

    file = request.files.get('file')
    if not file:
        flash("No file selected.", "danger")
        return redirect(url_for('chatbot_bp.index'))

    try:
        # Construct the OneDrive upload endpoint
        upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{file.filename}:/content"

        # Prepare headers for the upload request
        headers = {
            "Authorization": f"Bearer {user.onedrive_access_token}",
            "Content-Type": "application/octet-stream"
        }

        # Upload the file to OneDrive
        response = requests.put(upload_url, headers=headers, data=file.stream)

        # Handle the response
        if response.status_code == 201 or response.status_code == 200:
            uploaded_file = response.json()
            flash(f"File uploaded successfully to OneDrive: {uploaded_file['name']}", "success")
            print(session['chat_history'])
            response = {'sender': 'bot', 'text': 'File uploaded successfully '}
            session['chat_history'].append(response)
            
            
            user.chat_history = str(session['chat_history'])
            db.session.commit()
            
            print(session['chat_history'])
            
        else:
            print(f"Upload failed. Response: {response.text}")
            flash("Failed to upload file to OneDrive. Please try again later.", "danger")
    except Exception as e:
        print(f"Error uploading to OneDrive: {e}")
        flash("Failed to upload file to OneDrive. Please try again later.", "danger")

    return redirect(url_for('chatbot_bp.index'))

@chatbot_bp.route('/search_and_manage_files', methods=['POST'])
def search_and_manage_files():
    if 'user_id' not in session:
        return jsonify({"error": "You need to log in to access this feature."}), 401

    user = User.query.get(session['user_id'])
    if not user.onedrive_access_token:
        return jsonify({"error": "Please connect your OneDrive account first."}), 403

    query = request.form.get('query')
    if not query:
        bot_response = "Please enter a valid search query."
    else:
        search_results = search_files(query)  
        if isinstance(search_results, str):  
            bot_response = search_results
        else:
        
            
            files_list = "".join([
                f"""
                <div>
                    <strong>{file['name']}</strong>
                    <form method='POST' action='/chatbot/download_file/{file['id']}' style='display:inline;'>
                        <input type='hidden' name='csrf_token' value='{csrf.generate_csrf()}'>
                        <button type='submit'>Download</button>
                    </form>
                    
                    <form method='POST' action='/chatbot/share_file/{file['id']}' style='display:inline;'>
                        <input type='hidden' name='csrf_token' value='{csrf.generate_csrf()}'>
                        <input type='email' name='email' placeholder='Enter email' required>
                        <button type='submit'>Share</button>
                    </form>
                </div>
                """ 
                for file in search_results
            ])
            bot_response = files_list
    # Sohbet geçmişini güncelle
    chat_history = session.get('chat_history', [])
    chat_history.append({"sender": "user", "text": query})
    chat_history.append({"sender": "bot", "text": bot_response})
    session['chat_history'] = chat_history

    return render_template('chatbot.html', chat_history=chat_history, form=MessageForm(), show_search_form=False)

@chatbot_bp.route('/download_file/<file_id>', methods=['POST'])
def download_file(file_id):
    if 'user_id' not in session:
        return jsonify({"error": "You need to log in to access this feature."}), 401
    user = User.query.get(session['user_id'])
    if not user.onedrive_access_token:
        return jsonify({"error": "Please connect your OneDrive account first."}), 403
    # Try to download the file
    result = download_file_by_id(file_id)
    # Check if result is a file download (a Response object)
    if isinstance(result, Response):
        # Check the content type of the response
        content_type = result.headers.get('Content-Type', '')
        # Common MIME types for various file types
        if (
            'image/' in content_type or  # Images
            'application/pdf' in content_type or  # PDFs
            'application/octet-stream' in content_type or  
            'text/' in content_type or  
            'application/msword' in content_type or  # Microsoft Word files
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type or  
            'application/vnd.ms-excel' in content_type or  # Microsoft Excel
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type or   
            'application/vnd.ms-powerpoint' in content_type or  # Microsoft PowerPoint
            'application/vnd.openxmlformats-officedocument.presentationml.presentation' in content_type or  
            'audio/' in content_type or  # Audio 
            'video/' in content_type or  # Video 
            'application/zip' in content_type # ZIP 
          ):
            print(f"✅ Binary file with ID {file_id} (Content-Type: {content_type}) downloaded successfully for user {user.id}.")
            # Optionally update chat history before returning the file
            chat_history = session.get('chat_history', [])
            chat_history.append({"sender": "bot", "text": f"✅ File downloaded successfully"})
            session['chat_history'] = chat_history
            return result
        else:
            try:
                response_data = result.get_data(as_text=True)  # Get text from response, safe for non-binary files
            except Exception as e:
                print(f"Error while decoding response as text: {e}")
                response_data = None  # If decoding fails, assume the file is binary and not processable as text
            if response_data and "successfully" in response_data:
                bot_response = f"✅ File downloaded successfully"
            else:
                bot_response = f"❌ Failed to download file"
            # Update chat history
            chat_history = session.get('chat_history', [])
            chat_history.append({"sender": "bot", "text": bot_response})
            session['chat_history'] = chat_history
            return jsonify({"success": True, "message": bot_response})
    try:
        response_data = result.get_data(as_text=True)  # Get the plain text from the result
    except Exception as e:
        response_data = str(result)  # Handle edge case if result is not a Response object
    
    if response_data and "successfully" in response_data:
        bot_response = f"✅ File downloaded successfully"
    else:
        bot_response = f"❌ Failed to download file"
    # Update chat history
    chat_history = session.get('chat_history', [])
    chat_history.append({"sender": "bot", "text": bot_response})
    session['chat_history'] = chat_history
    return jsonify({"success": True, "message": bot_response})

@chatbot_bp.route('/share_file/<file_id>', methods=['POST'])
def share_file(file_id):
    if 'user_id' not in session:
        return jsonify({"error": "You need to log in to access this feature."}), 401
    user = User.query.get(session['user_id'])
    if not user.onedrive_access_token:
        return jsonify({"error": "Please connect your OneDrive account first."}), 403
    email = request.form.get('email')
    print(email)
    if not email:
        return jsonify({"error": "Please provide a valid email address to share the file."}), 400
    # File sharing process
    result = share_file_by_id(file_id, email, user.onedrive_access_token)
    if "successfully" in result:
        bot_response = f"✅ File successfully shared with {email}."
    else:
        bot_response = f"❌ Failed to share file with {email}."   
    # Update chat history
    chat_history = session.get('chat_history', [])
    chat_history.append({"sender": "user", "text": f"Share file with {email}"})  # Log the user's action
    chat_history.append({"sender": "bot", "text": bot_response})  # Log the bot's response
    session['chat_history'] = chat_history

    # Re-render the chatbot template and show the updated chat history
    return render_template('chatbot.html', chat_history=chat_history, form=MessageForm(), show_search_form=False)





































































