# Doable — To-Do App 📋

A clean, modern To-Do web application built with **Flask** and **SQLite**, featuring Google Authentication via Firebase, dark/light mode, due date management, and per-user task isolation.

---

## ✨ Features

- 🔐 **Email/Password signup and login** — passwords securely hashed
- 🔑 **Google Sign-in** — via Firebase Authentication
- 👤 **Per-user tasks** — each user sees only their own tasks
- 📅 **Due dates** — add a date to any task with overdue warnings
- 🔍 **Task filters** — filter by All / Pending / Done and by date
- 🌙 **Dark/Light mode** — theme preference saved in browser
- 📱 **Responsive design** — works on mobile and desktop

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite3 |
| Authentication | Firebase Auth (Google + Email/Password) |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Security | Werkzeug password hashing, python-dotenv |

---

## 📁 Project Structure

```
todo-app/
├── app.py                  # Flask backend — routes, auth, DB logic
├── .env                    # Secret keys (never committed to git)
├── .gitignore              # Ignores .env, tasks.db, venv, pycache
├── requirements.txt        # Python dependencies
├── tasks.db                # SQLite database (auto-created on first run)
├── static/
│   └── style.css           # All styling including dark/light mode
└── templates/
    ├── login.html          # Login page with Google sign-in
    ├── signup.html         # Signup page
    └── index.html          # Dashboard with task list and filters
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/nidhinjoy12/todo-app.git
cd todo-app
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Firebase

- Go to [console.firebase.google.com](https://console.firebase.google.com)
- Create a project and enable **Authentication**
- Enable **Email/Password** and **Google** sign-in providers
- Copy your Firebase API key from Project Settings

### 5. Create your `.env` file

Create a file called `.env` in the project root:

```
SECRET_KEY=your_random_secret_key_here
FIREBASE_API_KEY=your_firebase_api_key_here
DEBUG=True
```

To generate a strong secret key, run:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Run the app

```bash
python app.py
```

Open your browser and go to `http://localhost:5000`

---

## ⚙️ Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask session secret — use a long random string |
| `FIREBASE_API_KEY` | Firebase project API key for token verification |
| `DEBUG` | `True` for local development, `False` for production |

---

## 🔒 Security

- Passwords hashed using Werkzeug's `generate_password_hash`
- Firebase tokens verified server-side via Firebase REST API
- All tasks filtered by `user_id` — users cannot access each other's data
- Secrets loaded from `.env` — never hardcoded in source code
- `.env` and `tasks.db` excluded from git via `.gitignore`

---

## 📸 Pages

- **Login** — Email/password login + Google sign-in button
- **Signup** — Create a new account with username and password
- **Dashboard** — Add tasks, set due dates, filter by status or date, mark complete, delete

---

Built with 💚 using Flask + Firebase