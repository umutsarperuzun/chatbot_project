# 🤖 AI-Powered Chatbot with OneDrive Integration

## 🧩 Overview  
An intelligent, feature-rich chatbot application built with Flask, integrated with Microsoft OneDrive, and enhanced with NLP and sentiment analysis. It supports file operations, maintenance reporting, and vehicle management — all through an intuitive chat interface.

---

## 🚀 Key Features

- **🧠 Natural Language Processing (NLP):**  
  Understands and responds to user input intelligently using pre-trained models.

- **☁️ OneDrive Integration:**  
  Upload, search, download, and share files directly via the chatbot using the Microsoft OneDrive API.

- **🛠 Maintenance Reporting System:**  
  Users can submit and review maintenance reports for better issue tracking.

- **📈 Sentiment Analysis:**  
  Analyzes user messages and classifies them as *positive*, *neutral*, or *negative* using machine learning.

- **🚗 Vehicle Information Management:**  
  Tracks vehicle details, past maintenance, and upcoming service schedules.

- **👤 Session Management:**  
  Lightweight user recognition based on first and last name — no login required.

- **💬 Interactive Chat Interface:**  
  Clean and dynamic UI that mimics real-world chatbot experiences.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/UmutsUzun/chatbot_project.git
cd chatbot-project
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ **Note:** PyTorch is not included in `requirements.txt`. Install it separately:
```bash
pip install torch torchvision torchaudio
```
For GPU support, refer to the [official PyTorch installation guide](https://pytorch.org/get-started/locally/).

### 4. Environment Configuration  
Create a `.env` file in the root directory and add the following:
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
Open your browser and navigate to: `http://127.0.0.1:5000/`

---

## 💡 How to Use

- Enter your **first name** and **last name** to start a session.  
- Use intuitive commands such as:
  - `"Upload a file to OneDrive"`
  - `"Search for a file"`
  - `"Download a file"`
  - `"Report a maintenance issue"`
  - `"View maintenance reports"`
- The chatbot handles and responds using NLP and sentiment analysis.

---

## 🛠 Technologies Used

- **Backend:** Flask, SQLAlchemy  
- **Frontend:** Bootstrap, JavaScript  
- **Machine Learning:** PyTorch, CardiffNLP Sentiment Model  
- **Database:** PostgreSQL  
- **Cloud Storage:** Microsoft OneDrive API

---

## 🤝 Contributing

1. Fork the repository  
2. Create a new branch: `git checkout -b feature-branch`  
3. Commit your changes: `git commit -m "Add new feature"`  
4. Push to GitHub: `git push origin feature-branch`  
5. Open a **Pull Request**

---

## 📄 License  
MIT License — see the `LICENSE` file for details.

---

## 📬 Contact  
For support or inquiries:  
**Sarper Uzun** — `sarperuzun1@gmail.com`
