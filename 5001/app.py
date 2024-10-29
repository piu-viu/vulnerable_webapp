from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# PostgreSQL database URI format:
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@localhost/db5001'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Message model
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Home route that redirects to login
@app.route('/')
def home():
    return redirect('/login')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Sikker SQL-spørring med parametrisering for å unngå SQL injection
        query = text("SELECT * FROM users WHERE username = :username AND password = :password")
        with db.engine.connect() as connection:
            result = connection.execute(query, {"username": username, "password": password}).fetchone()

        if result:
            session['user'] = result[1]
            return redirect('/dashboard')
        else:
            return "Invalid login credentials"
    
    return render_template('login.html')

# Vulnerable dashboard page with Stored XSS example and Ping functionality
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    ping_result = ''
    if 'user' in session:
        if request.method == 'POST':
            if 'message' in request.form:
                # Save the user message to the database
                user_message = request.form['message']
                new_message = Message(username=session['user'], content=user_message)
                db.session.add(new_message)
                db.session.commit()
            elif 'ip' in request.form:
                # Command injection vulnerability (Ping)
                ip_address = request.form['ip']
                ping_command = f"ping -c 4 {ip_address}"
                ping_result = os.popen(ping_command).read()

        # Retrieve all messages
        messages = Message.query.all()
        
        # Render the dashboard with messages and ping results
        return render_template('dashboard.html', user=session['user'], messages=messages, ping_result=ping_result)
    
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

