from flask_sqlalchemy import SQLAlchemy
from extensions import db
db = SQLAlchemy()

class SafetyFeedback(db.Model):
    __tablename__ = 'safety_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    place = db.Column(db.String(100))  
    area_name = db.Column(db.String(100))
    safety_rating = db.Column(db.String(50))
    recommend_score = db.Column(db.String(10))
    police_patrol = db.Column(db.String(50))
    crime_witnessed = db.Column(db.String(50))
    crime_description = db.Column(db.Text)
    police_presence = db.Column(db.String(50))
    road_safety = db.Column(db.String(50))
    traffic_issues = db.Column(db.String(255))
    traffic_signs = db.Column(db.String(50))
    lighting = db.Column(db.String(50))
    security_cameras = db.Column(db.String(50))
    road_condition = db.Column(db.String(50))
    crowd = db.Column(db.String(50))
    suspicious_activity = db.Column(db.String(50))
    homeless_presence = db.Column(db.String(50))

    def __repr__(self):
        return f"<SafetyFeedback(place={self.place}, area_name={self.area_name})>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    user = db.relationship('User', backref=db.backref('contacts', lazy=True))
