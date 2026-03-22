from flask import Flask, render_template, request, redirect, session, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import sqlite3
import requests as req
from datetime import date
import os

# ✅ Load .env file first
load_dotenv()

app = Flask(__name__)

# ✅ Load secrets from .env — never hardcoded
app.secret_key = os.environ.get("SECRET_KEY")
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")

# ── DB Connection ────────────────────────────────────────
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("tasks.db")
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ── Home page ────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    db = get_db()

    tasks = db.execute(
        """
        SELECT * FROM tasks
        WHERE user_id = ?
        ORDER BY
            CASE WHEN due_date IS NULL OR due_date = '' THEN 1 ELSE 0 END,
            due_date ASC
        """,
        (user_id,)
    ).fetchall()

    today = date.today().isoformat()
    return render_template("index.html", tasks=tasks, today=today)

# ── Add task ─────────────────────────────────────────────
@app.route('/add', methods=['POST'])
def add():
    # ✅ Route protection — redirect if not logged in
    if 'user_id' not in session:
        return redirect('/login')

    task = request.form.get('task', '').strip()
    due_date = request.form.get('due_date', '')
    user_id = session['user_id']

    # ✅ Validate task is not empty or too long
    if not task or len(task) > 500:
        return redirect('/')

    db = get_db()
    db.execute(
        "INSERT INTO tasks (content, user_id, due_date) VALUES (?, ?, ?)",
        (task, user_id, due_date)
    )
    db.commit()
    return redirect('/')

# ── Delete task ──────────────────────────────────────────
@app.route('/delete/<int:id>')
def delete(id):
    # ✅ Route protection
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    db = get_db()
    db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (id, user_id)
    )
    db.commit()
    return redirect('/')

# ── Complete task ────────────────────────────────────────
@app.route('/complete/<int:id>')
def complete(id):
    # ✅ Route protection
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    db = get_db()
    db.execute(
        "UPDATE tasks SET completed = 1 WHERE id = ? AND user_id = ?",
        (id, user_id)
    )
    db.commit()
    return redirect('/')

# ── Signup ───────────────────────────────────────────────
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = generate_password_hash(request.form['password'])

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            db.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return render_template('signup.html', error="Username already exists. Try another.")

    return render_template('signup.html')

# ── Login ────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid username or password.")

    return render_template('login.html')

# ── Logout ───────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ── Firebase Google Login ────────────────────────────────
@app.route('/firebase-login', methods=['POST'])
def firebase_login():
    data = request.get_json()
    id_token = data.get('idToken')

    if not id_token:
        return jsonify({"status": "error", "message": "No token provided"}), 400

    verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}"
    response = req.post(verify_url, json={"idToken": id_token})
    firebase_data = response.json()

    if 'users' not in firebase_data:
        return jsonify({"status": "error", "message": "Invalid Firebase token"}), 401

    email = firebase_data['users'][0]['email']

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (email,)
    ).fetchone()

    if not user:
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (email, "firebase_user")
        )
        db.commit()

    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (email,)
    ).fetchone()

    session['user_id'] = user['id']
    return jsonify({"status": "success"})

# ── Init DB ──────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("tasks.db")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            user_id INTEGER,
            due_date TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    try:
        conn.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=os.environ.get("DEBUG", "False") == "True")