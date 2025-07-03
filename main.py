from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
#os.getenv("DB_CONN_STR")
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

app = Flask(__name__)
CORS(app)  # Enable CORS
app.template_folder = "templates"  # Flask uses this by default

# Home route (index.html)
@app.route('/')
def home():
    #return render_template('index.html')
    return "fix";

# Route to render dashboard.html
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Route to render event_form.html
@app.route('/event-form')
def event_form():
    return render_template('event_form.html')

# Route to render organizer.html
@app.route('/organizer')
def organizer():
    return render_template('organizer.html')

# Route to render register.html
@app.route('/register')
def register():
    return render_template('register.html')


# Get all events (returns JSON)
@app.route('/events', methods=['GET'])
def get_events():
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Events")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create a new event (via query params)
@app.route('/events', methods=['POST'])
def create_event():
    try:
        name = request.args.get('name')
        description = request.args.get('description')
        date = request.args.get('date')
        location = request.args.get('location')
        capacity = request.args.get('capacity')

        if not all([name, description, date, location, capacity]):
            return jsonify({"error": "Missing required query parameters"}), 400

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Events (name, description, date, location, capacity) VALUES (?, ?, ?, ?, ?)",
                name, description, date, location, int(capacity)
            )
            conn.commit()
            return jsonify({"message": "Event created successfully"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submit-event', methods=['POST'])
def submit_event():
    try:
        name = request.form['name']
        description = request.form['description']
        date = request.form['date']
        location = request.form['location']
        capacity = int(request.form['capacity'])

        # Optional: Insert into database here
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Events (name, description, date, location, capacity) VALUES (?, ?, ?, ?, ?)",
                name, description, date, location, capacity
            )
            conn.commit()

        return f"<h2>Event '{name}' created successfully!</h2><a href='/event-form'>Back</a>"
    except Exception as e:
        return f"<h2>Error: {str(e)}</h2><a href='/event-form'>Back</a>"

if __name__ == "__main__":
    app.run(debug=True)
