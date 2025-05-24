from flask import Blueprint, request, render_template, session, redirect, url_for, flash,Response
from microsoftgraph.client import Client
from models import db, User
import secrets
import msal
import requests
from fuzzywuzzy import fuzz
from sarper_secrets import CLIENT_ID, CLIENT_SECRET, get_secrets
# Blueprint 
onedrive_bp = Blueprint('onedrive_bp', __name__)

graph_client = get_secrets()

client_id = CLIENT_ID
client_secret = CLIENT_SECRET
authority = "https://login.microsoftonline.com/common"

@onedrive_bp.route('/login', methods=['GET'])
def login():
    try:
        # Check to user 
        user_id = session.get('user_id')
        if not user_id:
            flash("User not logged in. Please log in first.", "danger")
            return redirect(url_for('auth_bp.login'))

        # Get user to db
        user = User.query.get(user_id)
        if not user:
            flash("User not found. Please log in again.", "danger")
            return redirect(url_for('auth_bp.login'))

        # Create random state
        state = secrets.token_hex(16)
        user.state = state
        db.session.commit()

        print(f"Generated state for user {user.username}: {state}")

      
        scope = ["User.Read", "Files.ReadWrite.All", "Mail.Send"]
        auth_url = graph_client.authorization_url(
            scope=scope,
            state=state,
            redirect_uri="http://localhost:5000/onedrive/callback"
        )
        print("Generated Authorization URL:", auth_url)  

        return redirect(auth_url)
    except Exception as e:
        print(f"Error in login: {e}")
        flash("Failed to initiate login process. Please try again later.", "danger")
        return redirect(url_for('auth_bp.login'))


@onedrive_bp.route('/callback', methods=['GET'])
def callback():
    try:
        
        returned_state = request.args.get('state')
        user_id = session.get('user_id')
        if not user_id:
            flash("User not logged in. Please log in first.", "danger")
            return redirect(url_for('auth_bp.login'))

        user = User.query.get(user_id)
        if not user:
            flash("User not found. Please log in again.", "danger")
            return redirect(url_for('auth_bp.login'))

        print(f"Returned State: {returned_state}")
        print(f"User's Saved State: {user.state}")

        
        if returned_state != user.state:
            flash("Invalid state parameter. Possible CSRF attack detected.", "danger")
            print("State mismatch detected.")
            return redirect(url_for('auth_bp.login'))

        #  Get Authorization code
        code = request.args.get('code')
        print(f"Authorization Code: {code}")
        if not code:
            flash("Authorization failed: No authorization code returned.", "danger")
            return redirect(url_for('auth_bp.login'))

        
        app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret,
        )

        tokens = app.acquire_token_by_authorization_code(
            code=code,
            scopes=["User.Read", "Files.ReadWrite.All", "Mail.Send"],
            redirect_uri="http://localhost:5000/onedrive/callback"
        )

        
        if 'access_token' not in tokens:
            print("Error: Access token not found in response.")
            flash("Failed to authenticate with Microsoft. Please try again later.", "danger")
            return redirect(url_for('auth_bp.login'))

        print(f"Tokens retrieved for user {user.username}: {tokens}")

        # Save token
        user.onedrive_access_token = tokens.get('access_token')
        user.onedrive_refresh_token = tokens.get('refresh_token')
        user.state = None  
        db.session.commit()

        flash("Successfully connected to OneDrive!", "success")
        return redirect(url_for('chatbot_bp.index'))
    except Exception as e:
        print(f"Error in callback: {e}")
        flash("Failed to authenticate with Microsoft. Please try again later.", "danger")
        return redirect(url_for('auth_bp.login'))

   
#############################Perform OneDrive Actions############################

def perform_onedrive_action(action, user_message):
    
    if 'user_id' not in session:
        return "Please log in to access OneDrive functionality."

    user = User.query.get(session['user_id'])
    if not user.onedrive_access_token:
        return redirect(url_for('onedrive_bp.login'))

    print(f"Access Token: {user.onedrive_access_token}")

    graph_client.set_token(user.onedrive_access_token)  #Set to sdk s

    # Handle valid actions
    if action == "upload":
        return render_template("uploadd.html")
    
    elif action == "search":
        query = extract_query(user_message)
        if query:
            search_results = search_files(query)
            if isinstance(search_results, str):
                return search_results
            return render_template('search_manage_files.html', files=search_results)
        else:
            return "Please specify what you want to search for."

    elif action == "download":
        file_id = extract_file_id(user_message)
        if file_id:
            return download_file_by_id(file_id)
        else:
            return "Please specify a valid file to download."

    elif action == "share":
        file_id = extract_file_id(user_message)
        if file_id:
            return share_file_by_id(file_id)
        else:
            return "Please specify a valid file to share."
    
    else:
        return "Invalid OneDrive action requested."
   
########################UTILITY FUNCTIONS###############################
def extract_file_id(user_message):
    
    words = user_message.split()
    if "file_id:" in words:
        return words[words.index("file_id:") + 1]
    return None

def extract_query(user_message):
    
    words = user_message.split()
    if "search" in words:
        return " ".join(words[words.index("search") + 1:])
    return None

######################HELPER FUNCTIONS################################

def upload_file(file):
    try:
        
        with file.stream as file_data:
            response = graph_client.drive_item.upload_file("/", file.filename, file_data)
        return f"File '{file.filename}' uploaded successfully!"
    except Exception as e:
        return f"Failed to upload file '{file.filename}'. Error: {str(e)}"

def search_files(query):
    try:
        
        user = User.query.get(session['user_id'])
        access_token = user.onedrive_access_token

        search_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(search_url, headers=headers)

        if response.status_code == 200:
            results = response.json()
            
    
            files = results.get('value', [])
            if not files:
                print("No files found matching your query.")
                return "No files found matching your query."

            # Check to search result come from fuzzy matching
            matched_files = []
            for file in files:
                
                # FILTER
                if query.lower() in file['name'].lower():
                    similarity_score = fuzz.partial_ratio(file['name'].lower(), query.lower())
                    print(f"Checking file '{file['name']}' with similarity score: {similarity_score}")
                    if similarity_score > 50:  # Benzerlik eşiğini esnettik
                        matched_files.append(file)

            if not matched_files:
                return "No files found with sufficient similarity to your query."

            # print("Matched Search Results:", matched_files)  
            return matched_files

        else:
            return f"Failed to search files. Error: {response.text}"

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return f"Failed to search files. Error: {str(e)}"

def download_file_by_id(file_id):
    try:
        # Acess to token
        user = User.query.get(session['user_id'])
        if not user or not user.onedrive_access_token:
            return "No valid access token available. Please reconnect to OneDrive."

        
        download_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
        headers = {
            "Authorization": f"Bearer {user.onedrive_access_token}"
        }
        # Send request
        response = requests.get(download_url, headers=headers, stream=True)
        
        if response.status_code == 200:
            

            return Response(
                response.content,
                headers={
                    'Content-Disposition': f'attachment;filename={file_id}.file',
                    'Content-Type': response.headers['Content-Type']
                }
            )
        else:
            return f"Failed to download file. Error: {response.text}"
    except Exception as e:
        return f"Failed to download file. Error: {str(e)}"
    
    
def send_email_via_graph_api(recipient_email, share_link, user_access_token):
    try:
        
        email_url = "https://graph.microsoft.com/v1.0/me/sendMail"
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "message": {
                "subject": "File Shared via OneDrive",
                "body": {
                    "contentType": "Text",
                    "content": f"Here is the link to the file you requested: {share_link}"
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": recipient_email
                        }
                    }
                ]
            },
            "saveToSentItems": "true"
        }

        response = requests.post(email_url, headers=headers, json=body)

        if response.status_code == 202:
            print(f"E-posta gönderildi: {recipient_email}")
            return "Email sent successfully."
        else:
            print(f"E-posta gönderme hatası: {response.status_code} - {response.text}")
            return f"Failed to send email. Error: {response.status_code} - {response.text}"

    except Exception as e:
        print(f"E-posta gönderim hatası: {str(e)}")
        return f"Failed to send email. Error: {str(e)}"
    
def share_file_by_id(file_id, recipient_email, user_access_token):
    try:
        
        share_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/createLink"
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "type": "view",
            "scope": "anonymous"  
        }

        
        response = requests.post(share_url, headers=headers, json=body)
        if response.status_code == 200:
            share_link = response.json()['link']['webUrl']
            print(f"Share link created: {share_link}")

            
            send_email_via_graph_api(recipient_email, share_link, user_access_token)

            return "File shared successfully!"
        else:
            return f"Failed to create share link. Error: {response.text}"

    except Exception as e:
        return f"Failed to share file. Error: {str(e)}"
   
##############################ROUTES###########################################


@onedrive_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    print('0000000')
    
    if 'user_id' not in session:
        flash("Please log in to access OneDrive.", "warning")
        return redirect(url_for('auth_bp.login'))

    user = User.query.get(session['user_id'])
    if not user.onedrive_access_token:
        flash("Please connect your OneDrive account first.", "danger")
        return redirect(url_for('onedrive_bp.login'))
    
    if request.method == "POST":
        
        file = request.files.get('file')
        if not file:
            flash("No file selected.", "danger")
            return redirect(url_for('onedrive_bp.upload'))

        
        graph_client.set_token(user.onedrive_access_token)
        result_message = upload_file(file)
        if "successfully" in result_message:
            flash(result_message, "success")
        else:
            flash(result_message, "danger")

    return render_template("upload.html")


@onedrive_bp.route('/search_and_manage_files', methods=['GET', 'POST'])
def search_and_manage_files():
    if 'user_id' not in session:
        flash("Please log in to access OneDrive features.", "warning")
        return redirect(url_for('auth_bp.login'))
    
    user = User.query.get(session['user_id'])
    if not user.onedrive_access_token:
        flash("Please connect your OneDrive account first.", "danger")
        return redirect(url_for('onedrive_bp.login'))
    
    if request.method == 'POST':
        query = request.form.get('query')
        print(query)
        if not query:
            flash("Please enter a query to search for files.", "danger")
            return redirect(url_for('onedrive_bp.search_and_manage_files'))
        
        
        search_results = search_files(query)
        print("Search Results:", search_results)  
        
        if isinstance(search_results, str):
            
            flash(search_results, "danger")
            return redirect(url_for('onedrive_bp.search_and_manage_files'))
        
        return render_template('search_manage_files.html', files=search_results)

    return render_template('search_manage_files.html')

@onedrive_bp.route('/download_file/<file_id>', methods=['POST'])
def download_file(file_id):
    if 'user_id' not in session:
        flash("Please log in to access OneDrive.", "warning")
        return redirect(url_for('auth_bp.login'))

    user = User.query.get(session['user_id'])
    if not user.onedrive_access_token:
        flash("Please connect your OneDrive account first.", "danger")
        return redirect(url_for('onedrive_bp.login'))

    
    try:
        download_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
        headers = {
            "Authorization": f"Bearer {user.onedrive_access_token}"
        }

        
        response = requests.get(download_url, headers=headers, stream=True)

        
        if response.status_code == 200:
            return Response(
                response.content,
                headers={
                    'Content-Disposition': f'attachment;filename={file_id}.file',
                    'Content-Type': response.headers['Content-Type']
                }
            )
        else:
            flash("Failed to download the file.", "danger")
    except Exception as e:
        flash(f"Failed to download the file. Error: {str(e)}", "danger")

    return redirect(url_for('onedrive_bp.search_and_manage_files'))


@onedrive_bp.route('/share_file/<file_id>', methods=['POST'])
def share_file(file_id):
    if 'user_id' not in session:
        flash("Please log in to access OneDrive.", "warning")
        return redirect(url_for('auth_bp.login'))

    user = User.query.get(session['user_id'])
    if not user.onedrive_access_token:
        flash("Please connect your OneDrive account first.", "danger")
        return redirect(url_for('onedrive_bp.login'))

    recipient_email = request.form.get('email')
    if not recipient_email:
        flash("Recipient email is required to share the file.", "danger")
        return redirect(url_for('onedrive_bp.search_and_manage_files'))

    
    graph_client.set_token(user.onedrive_access_token)
    result = share_file_by_id(file_id, recipient_email, user.onedrive_access_token)

    if "successfully" in result.lower():
        flash(result, "success")
    else:
        flash(result, "danger")

    return redirect(url_for('onedrive_bp.search_and_manage_files'))

























































