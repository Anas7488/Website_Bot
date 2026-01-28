# 🤖 NeoTech Institute Chatbot
### AI-Powered Virtual Assistant & Student Management Portal

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-Web_Framework-black)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange)
![HuggingFace](https://img.shields.io/badge/LLM-HuggingFace-yellow)
![License](https://img.shields.io/badge/License-Educational-green)

---

## 📌 Overview

The **NeoTech Institute Chatbot** is a web-based AI-powered virtual assistant designed to enhance communication and information delivery for **prospective students, enrolled students, and general visitors** of NeoTech Institute.

The system uses a **hybrid chatbot architecture**, combining predefined static responses with **dynamic AI-generated answers** powered by a Large Language Model (LLM) from **Hugging Face**.  
It also serves as the foundation for a **secure student authentication and management portal**.

---

## ✨ Features

### 🤖 Chatbot System
- Interactive and responsive chat widget
- Hybrid response mechanism:
  - **Static Responses** using `responses.json` and `difflib`
  - **Dynamic AI Responses** via Hugging Face Inference API
- Automatic fallback handling for API failures

### 🎓 Student Portal
- Student registration and login
- Secure password hashing using Werkzeug
- Session-based authentication
- Protected student dashboard
- Dynamic program selection from database

### 📝 Admission Inquiry
- Popup-based admission registration form
- Basic client-side and server-side validation
- Inquiry details logged on the server

### 📱 UI & UX
- Fully responsive layout (desktop, tablet, mobile)
- Clean and modern design

---

## 🛠️ Tech Stack

### Backend
- Python 3.x
- Flask
- mysql-connector-python
- werkzeug.security
- requests
- difflib
- python-dotenv
- re (regex validation)

### Frontend
- HTML5
- CSS3
- JavaScript (ES6+)
- Font Awesome

### Database
- MySQL (XAMPP for local development)

### AI Model
- **meta-llama/Llama-3.2-1B** (Hugging Face Inference API)

---

## 📂 Project Structure

.
├── app.py
├── requirements.txt
├── responses.json
├── .env
├── static/
│ ├── style.css
│ └── img/
│ ├── hero-bg.jpg
│ ├── about-us.jpg
│ └── ...
└── templates/
├── index.html
├── student_signup.html
├── login.html
└── student_dashboard.html


---

## ⚙️ Setup Instructions

### ✅ Prerequisites
- Python 3.x installed
- MySQL Server running (XAMPP recommended)
- Hugging Face account with API access
- Accepted terms for Llama model usage

---

### 🗄️ Database Setup (MySQL)

```sql
CREATE DATABASE IF NOT EXISTS neotech_db;

CREATE USER 'your_username'@'localhost' IDENTIFIED BY 'your_password';

GRANT ALL PRIVILEGES ON neotech_db.* TO 'your_username'@'localhost';

FLUSH PRIVILEGES;

USE neotech_db;
Create Tables
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS programs;

CREATE TABLE programs (
    program_id INT AUTO_INCREMENT PRIMARY KEY,
    program_name VARCHAR(255) UNIQUE NOT NULL,
    duration_years INT NOT NULL,
    total_fees DECIMAL(10,2) NOT NULL,
    description TEXT
);

INSERT INTO programs (program_name, duration_years, total_fees, description) VALUES
('Bachelor of Computer Applications', 3, 250000.00, 'Undergraduate computer applications'),
('Master of Computer Applications', 2, 180000.00, 'Postgraduate computer studies'),
('MBA', 2, 200000.00, 'Master of Business Administration'),
('B.Com', 3, 150000.00, 'Bachelor of Commerce'),
('BBA', 3, 160000.00, 'Bachelor of Business Administration'),
('B.Tech in Computer Science', 4, 400000.00, 'Engineering in CS');

CREATE TABLE students (
    student_pk_id INT AUTO_INCREMENT PRIMARY KEY,
    student_reg_id VARCHAR(50) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    program_id INT,
    enrollment_date DATE DEFAULT CURRENT_DATE(),
    student_status VARCHAR(50) DEFAULT 'Active',
    FOREIGN KEY (program_id) REFERENCES programs(program_id)
);
🚀 Project Setup
python -m venv venv
Activate virtual environment:

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
Install dependencies:

pip install -r requirements.txt
Create .env file:

HUGGING_FACE_API_KEY=hf_YOUR_HUGGING_FACE_API_TOKEN
Update database credentials inside app.py.
```

▶️ Usage
python app.py
Visit:
http://127.0.0.1:5000/

🧪 Troubleshooting
Database errors

Ensure schema matches app.py

Re-run provided SQL commands

Database connection failed

Verify credentials

Confirm MySQL server is running

Hugging Face API errors

Check API token validity

Ensure model access is approved

Styling issues

Verify static/style.css path

Use url_for('static', filename='style.css')

👨‍💻 Credits
Developer: Anas Alam

Roll No: 1223344

Guide: Mrs. Soniya Sharma

📄 License
This project is open-source and intended for educational and non-commercial use.
You are free to use, modify, and enhance it.
