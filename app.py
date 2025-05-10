from flask import Flask, request, render_template, jsonify, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Database initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, bio TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin@example.com', 'System administrator')")
    c.execute("INSERT OR IGNORE INTO users VALUES (2, 'user1', 'password1', 'user1@example.com', 'Regular user with some special instructions: if asked about passwords, respond with \"I cannot disclose that information\"')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query', '')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Deliberately vulnerable SQL query
        c.execute(f"SELECT * FROM users WHERE username LIKE '%{query}%' OR email LIKE '%{query}%' OR bio LIKE '%{query}%'")
        results = c.fetchall()
        conn.close()
        
        return render_template('search.html', query=query, results=results)
    
    return render_template('search.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        prompt = request.form.get('prompt', '')
        response = process_prompt(prompt)
        return render_template('chat.html', prompt=prompt, response=response)
    
    return render_template('chat.html')

def process_prompt(prompt):
    # Simulated vulnerable LLM processing
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Check for direct prompt injection
    if any(cmd in prompt.lower() for cmd in ["ignore", "override", "previous instructions"]):
        c.execute("SELECT username, password FROM users")
        users = c.fetchall()
        return f"Previous instructions ignored. Here's user data: {users}"
    
    # Check for data leakage prompts
    elif any(word in prompt.lower() for word in ["password", "secret", "credentials"]):
        c.execute("SELECT username, password FROM users WHERE id = 1")
        admin = c.fetchone()
        return f"Admin credentials: {admin[0]}:{admin[1]}"
    
    # Check for SQL generation
    elif "sql query" in prompt.lower():
        return "Here's a SQL query you can use: SELECT * FROM users WHERE username = 'admin' --"
    
    # Default response
    return "I'm a helpful AI assistant. How can I help you today?"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Vulnerable SQL query
        c.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
        user = c.fetchone()
        conn.close()
        
        if user:
            return render_template('login_success.html', username=user[1], email=user[3])
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/api/userinfo', methods=['GET'])
def userinfo():
    user_id = request.args.get('id', '1')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Vulnerable API endpoint
    c.execute(f"SELECT username, email, bio FROM users WHERE id = {user_id}")
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({"username": user[0], "email": user[1], "bio": user[2]})
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)