from flask import Flask, render_template, request, redirect
from models import db, Event, Registration
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)

@app.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get(event_id)
    return render_template('event_form.html', event=event)

@app.route('/register', methods=['POST'])
def register():
    registration = Registration(
        attendee_name=request.form['name'],
        contact=request.form['contact'],
        event_id=request.form['event_id']
    )
    db.session.add(registration)
    db.session.commit()
    return redirect('/')

@app.route('/admin')
def admin_dashboard():
    events = Event.query.all()
    return render_template('dashboard.html', events=events)

@app.route('/admin/create', methods=['POST'])
def create_event():
    event = Event(
        name=request.form['name'],
        description=request.form['description'],
        location=request.form['location'],
        date=request.form['date'],
        capacity=request.form['capacity']
    )
    db.session.add(event)
    db.session.commit()
    return redirect('/admin')

@app.route('/admin/delete/<int:id>')
def delete_event(id):
    event = Event.query.get(id)
    db.session.delete(event)
    db.session.commit()
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
