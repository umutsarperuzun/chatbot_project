# AI-Powered Chatbot with Sentiment Analysis and OneDrive Integration

This project is an AI-powered chatbot tailored for tasks such as fleet management, maintenance reporting, and document operations. It features machine learning-driven sentiment analysis and integrates seamlessly with Microsoft OneDrive for cloud-based file management.

---

## Features

* **Natural Language Processing (NLP):** Facilitates intuitive user interaction.
* **Sentiment Analysis:** Automatically classifies messages as positive, neutral, or negative.
* **Vehicle & Maintenance Management:** Log and retrieve reports efficiently.
* **Microsoft OneDrive Integration:** Enables file upload, download, and sharing directly via cloud.

---

## Prerequisites

To run this project, ensure you have the following:

* Python 3.9+
* A MySQL database server
* Access to Microsoft Azure to register an application for OneDrive API usage
* Required Python packages (`requirements.txt`)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Install Dependencies

Install the necessary Python packages:

```bash
pip install -r requirements.txt
```

### 3. Set Up the Database

* Import the SQL schema to your MySQL database:

```bash
mysql -u <username> -p <database_name> < chatbot_db.sql
```

* Update the database connection settings in `config.py`.

### 4. Configure OneDrive Integration (User-Provided Credentials)

To ensure user privacy and application security, we no longer hardcode OneDrive API credentials into the application. Instead, each user must register their own application on the [Microsoft Azure Portal](https://portal.azure.com/) and obtain a **Client ID** and **Client Secret**.

**Steps to Configure:**

1. Go to Azure Portal → Azure Active Directory → App registrations.
2. Register a new application.
3. Under “Authentication,” set the appropriate redirect URIs.
4. Under “Certificates & secrets,” generate a **Client Secret**.
5. Copy the **Client ID** and **Client Secret**.

Once obtained, the credentials can be passed to the application securely. Here’s a code snippet showing where to apply them:

```python
from microsoftgraph.client import Client

CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"

def get_secrets():
    return Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
```

Replace `"your-client-id"` and `"your-client-secret"` with your own values, or implement a secure prompt or environment variable method if preferred.

> 🔒 **Note**: These credentials are user-specific and not shared publicly for privacy and security.

### 5. Run the Application

Start the Flask development server:

```bash
python app.py
```

Access the chatbot at `http://127.0.0.1:5000`.

---

## Project Structure

* `app.py`: Main application entry point.
* `config.py`: Configuration settings for database and API.
* `models.py`: ORM definitions and schema.
* `routes/`: Contains Flask route handlers.
* `templates/`: Front-end HTML interface.
* `static/`: CSS, JavaScript, and media files.
* `requirements.txt`: Python dependencies.

---

## How to Use

1. Start the server and open your browser at `http://127.0.0.1:5000`.
2. Interact with the chatbot to:

   * Upload/download/search files via OneDrive.
   * Log and check vehicle maintenance reports.
   * Access vehicle data on demand.

---

## Contact

For questions or support, contact:

* 📧 Email: \[sarperuzun1@gmail.com]


