from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(300))
    location = db.Column(db.String(100))
    date = db.Column(db.String(50))
    capacity = db.Column(db.Integer)
    registrations = db.relationship('Registration', backref='event', lazy=True)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attendee_name = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
