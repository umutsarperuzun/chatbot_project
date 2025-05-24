AI-Powered Chatbot with Sentiment Analysis and OneDrive Integration

This project is an AI-powered chatbot designed to streamline operations like fleet management, maintenance reporting, and document handling. The system also includes machine learning-based sentiment analysis and integrates with Microsoft OneDrive for seamless cloud storage operations.

---

Features:
- Natural Language Processing (NLP) for user-friendly interactions.
- Sentiment analysis to detect positive, neutral, or negative sentiments in user messages.
- Vehicle management and maintenance reporting functionalities.
- Integration with OneDrive for file upload, download, and sharing.

---

Prerequisites:
To run the project, you need:
- Python 3.9+
- A MySQL database server
- OneDrive API credentials
- Required Python packages (see `requirements.txt`)

---

Setup Instructions:

1. Clone the Repository:
   ```
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install Dependencies:
   Install the necessary Python libraries:
   ```
   pip install -r requirements.txt
   ```

3. Set Up the Database:
   - Import the SQL schema file to your MySQL server:
     ```
     mysql -u <username> -p <database_name> < chatbot_db.sql
     ```
   - Update the database connection settings in the `config.py` file.

4. Configure OneDrive Integration:
   - Add your OneDrive API credentials (client ID and client secret) to the `config.py` file.

5. Run the Application:
   Start the Flask development server:
   ```
   python app.py
   ```
   The chatbot will be accessible at `http://127.0.0.1:5000`.

---

Project Structure:
- `app.py`: Main application entry point.
- `config.py`: Configuration file for database and API credentials.
- `models.py`: Database models and schema definitions.
- `routes/`: Contains Flask routes for chatbot functionalities.
- `templates/`: HTML files for the web interface.
- `static/`: CSS, JavaScript, and image files.
- `requirements.txt`: List of required Python packages.

---

How to Use:
1. Launch the application in your browser (`http://127.0.0.1:5000`).
2. Interact with the chatbot to:
   - Search, upload, or download files via OneDrive.
   - Create or query maintenance reports.
   - Retrieve vehicle information.

---

Contact:
For any questions or issues, please contact:
- Email: [your-email@example.com]

---
