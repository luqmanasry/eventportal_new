from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = 'super-secret-key'
app.template_folder = "templates"

# Connection string to Azure SQL
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=tcp:eventhorizondatabase-sql.database.windows.net,1433;"
    "DATABASE=eventhorizonDB;"
    "UID=Admin1;"
    "PWD=Luqman123;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

# Home Page
@app.route('/')
def home():
    return render_template('index.html', role=session.get('role'))

# Register Account Page
@app.route('/register-account')
def register_account():
    return render_template('register_account.html')

# Handle Register POST
@app.route('/do-register', methods=['POST'])
def do_register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    hashed_password = generate_password_hash(password)

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Users (username, email, password, role) VALUES (?, ?, ?, ?)",
                username, email, hashed_password, role
            )
            conn.commit()
        return "<h2>Account created successfully!</h2><a href='/login'>Go to Login</a>"
    except Exception as e:
        return f"<h2>Error: {str(e)}</h2><a href='/register-account'>Try Again</a>"

# Login Page
@app.route('/login')
def login():
    return render_template('login.html')

# Handle Login POST
@app.route('/do-login', methods=['POST'])
def do_login():
    email = request.form['email']
    password = request.form['password']

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE email = ?", email)
            row = cursor.fetchone()
            if row and check_password_hash(row[3], password):
                session['user_id'] = row[0]
                session['username'] = row[1]
                session['role'] = row[4]
                return redirect('/')
            else:
                return "<h2>Invalid credentials</h2><a href='/login'>Try Again</a>"
    except Exception as e:
        return f"<h2>Error: {str(e)}</h2><a href='/login'>Back</a>"

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# View Events (JSON)
@app.route('/events', methods=['GET'])
def get_events():
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Events")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return jsonify([dict(zip(columns, row)) for row in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get registrations for a specific event (used by frontend toggle)
@app.route('/api/event-registrations/<int:event_id>')
def api_event_registrations(event_id):
    if session.get('role') != 'organizer':
        return jsonify([])

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.username FROM users u
                JOIN registrations r ON u.id = r.user_id
                WHERE r.event_id = ?
            """, event_id)
            users = [row[0] for row in cursor.fetchall()]
            return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Event Registration (User only)
@app.route('/event-register/<int:event_id>', methods=['POST'])
def event_register(event_id):
    if 'user_id' not in session or session['role'] != 'user':
        return redirect('/login')

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Registrations (user_id, event_id) VALUES (?, ?)",
                           session['user_id'], event_id)
            conn.commit()
        return render_template('event_register.html')  # Show success page
    except Exception as e:
        return f"<h2>Error: {str(e)}</h2><a href='/'>Back</a>"

# View Registration List (Organizer only)
@app.route('/view-registrations/<int:event_id>')
def view_registrations(event_id):
    if session.get('role') != 'organizer':
        return redirect('/')

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.username FROM users u
                JOIN registrations r ON u.id = r.user_id
                WHERE r.event_id = ?
            """, event_id)
            users = [row[0] for row in cursor.fetchall()]
            return render_template('view_registrations.html', users=users)
    except Exception as e:
        return f"<h2>Error: {str(e)}</h2><a href='/'>Back</a>"

# Create Event Form (Organizer only)
@app.route('/event-form')
def event_form():
    if session.get('role') != 'organizer':
        return redirect('/')
    return render_template('event_form.html')

# Submit Event (Organizer only)
@app.route('/submit-event', methods=['POST'])
def submit_event():
    if session.get('role') != 'organizer':
        return redirect('/')

    try:
        name = request.form['name']
        description = request.form['description']
        date = request.form['date']
        location = request.form['location']
        capacity = int(request.form['capacity'])

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Events (name, description, date, location, capacity) VALUES (?, ?, ?, ?, ?)",
                name, description, date, location, capacity
            )
            conn.commit()
        return redirect('/')
    except Exception as e:
        return f"<h2>Error: {str(e)}</h2><a href='/event-form'>Back</a>"

# Edit Event Page (Organizer only)
@app.route('/edit-event/<int:event_id>')
def edit_event(event_id):
    if session.get('role') != 'organizer':
        return redirect('/')

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Events WHERE id = ?", event_id)
            row = cursor.fetchone()
            if not row:
                return f"<h2>No event found with ID {event_id}</h2><a href='/'>Back</a>"
            columns = [column[0] for column in cursor.description]
            return render_template('edit_event.html', event=dict(zip(columns, row)))
    except Exception as e:
        return f"<h2>Error: {str(e)}</h2><a href='/'>Back</a>"

# Update Event (Organizer only)
@app.route('/update-event/<int:event_id>', methods=['POST'])
def update_event(event_id):
    if session.get('role') != 'organizer':
        return redirect('/')

    try:
        name = request.form['name']
        description = request.form['description']
        date = request.form['date']
        location = request.form['location']
        capacity = int(request.form['capacity'])

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Events 
                SET name = ?, description = ?, date = ?, location = ?, capacity = ? 
                WHERE id = ?
            """, name, description, date, location, capacity, event_id)
            conn.commit()
        return render_template('update_success.html')
    except Exception as e:
        return f"<h2>Error: {str(e)}</h2><a href='/edit-event/{event_id}'>Back</a>"

# Delete Event (Organizer only)
@app.route('/delete-event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    if session.get('role') != 'organizer':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Events WHERE id = ?", event_id)
            conn.commit()
        return jsonify({"message": "Event deleted"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=8000)
