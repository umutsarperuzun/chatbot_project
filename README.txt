# Chatbot project 

## Overview
This is an AI-powered chatbot with OneDrive integration, maintenance reporting, sentiment analysis, and file management features. The chatbot interacts with users, processes natural language inputs, and provides intelligent responses. It is integrated with Microsoft OneDrive for file operations and includes machine learning-based sentiment analysis to enhance interactions. 

## Features
- **Natural Language Processing (NLP)**: Understands and responds to user inputs.
- **OneDrive Integration**: Upload, search, download, and share files directly within the chatbot.
- **Maintenance Reporting System**: Users can submit and review maintenance reports.
- **Sentiment Analysis**: Analyzes user messages to classify them as positive, negative, or neutral.
- **Vehicle Information Management**: Tracks vehicle details, last maintenance, and upcoming schedules.
- **User Session Management**: Identifies users based on their input (first name & last name) without requiring a login system.
- **Interactive Chat Interface**: Displays chatbot messages and user interactions seamlessly.

## Installation
To run the chatbot, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/UmutsUzun/chatbot_project.git
cd chatbot-project
```
### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note:** The repository does not include PyTorch. You must install it separately:
```bash
pip install torch torchvision torchaudio
```
For GPU support, visit the official [PyTorch installation guide](https://pytorch.org/get-started/locally/).

### 4. Set Up Environment Variables
Create a `.env` file in the root directory and configure the required environment variables:
```env
ONEDRIVE_CLIENT_ID=your_client_id
ONEDRIVE_CLIENT_SECRET=your_client_secret
ONEDRIVE_REDIRECT_URI=your_redirect_uri
DATABASE_URL=your_database_url
```

### 5. Run Database Migrations
```bash
flask db upgrade
```

### 6. Start the Application
```bash
flask run
```
The chatbot will be accessible at `http://127.0.0.1:5000/`.

## Usage
- Open the chatbot interface in your browser.
- Enter your first and last name to initiate a session.
- Use commands like:
  - "Upload a file to OneDrive"
  - "Search for a file"
  - "Download a file"
  - "Report a maintenance issue"
  - "View maintenance reports"
- The chatbot processes and responds based on its NLP model and integrated functionalities.

## Technologies Used
- **Backend:** Flask, SQLAlchemy
- **Frontend:** Bootstrap, JavaScript
- **Machine Learning:** PyTorch, CardiffNLP sentiment analysis model
- **Database:** PostgreSQL
- **Cloud Storage:** Microsoft OneDrive API

## Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact
For any inquiries or support, contact **Sarper Uzun** at `sarperuzun1@gmail.com`.
