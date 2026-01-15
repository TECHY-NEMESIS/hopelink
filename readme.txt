🌱 HopeLink – Mental Health SOS Support System

HopeLink is a **Python Tkinter + MySQL based desktop application** designed to connect people in emotional distress with volunteers in real time.  
Users can post SOS messages, which are analyzed for emotional severity and then claimed by volunteers who can chat and provide support.

---

## ✨ Features

### 👤 User
- Register as a user
- Post SOS messages
- Automatic **emotion analysis** (happy / low / high)
- View own SOS posts
- Real-time chat with assigned volunteer

### 🧑‍🤝‍🧑 Volunteer
- Register as volunteer
- View unclaimed SOS posts
- Priority sorting based on emotion level
- Claim SOS requests
- Chat with users in real time

### 🧠 Emotion Detection
- Keyword-based emotion analysis
- Detects:
  - **High distress** (suicidal, hopeless, panic, etc.)
  - **Low distress**
  - **Happy / Neutral**

---

## 🛠️ Tech Stack

- **Python 3**
- **Tkinter** (GUI)
- **MySQL**
- `mysql-connector-python`

---

## 📁 Database Structure

### `users`
```sql
user_id INT PRIMARY KEY AUTO_INCREMENT
username VARCHAR(100)
role ENUM('user','volunteer')


HOW TO ACCESS THE FILE 
  
    Clone the repository

git clone https://github.com/yourusername/HopeLink.git
cd HopeLink

Install dependencies 

pip install mysql-connector-python


Setup MySQL database 

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "hopelink"
}


-----RUN THE APPLICATION-----