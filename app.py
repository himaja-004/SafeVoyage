import sqlite3
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from generate_map import generate_route_map
from models import SafetyFeedback, db, User, EmergencyContact
from sos_sender import send_sos_alert_fast2sms
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__) 
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
Migrate(app, db)

with app.app_context():
    db.create_all()

def convert_safety_rating(rating):
    mapping = {
        'Very Unsafe': 1,
        'Unsafe': 2,
        'Neutral': 3,
        'Safe': 4,
        'Very Safe': 5
    }
    return mapping.get(rating, 0)

def convert_recommend_score(answer):
    return 5 if answer == 'Yes' else 0

def convert_police_patrol(patrol):
    mapping = {
        'Rarely': 2,
        'Sometimes': 3,
        'Frequently': 5
    }
    return mapping.get(patrol, 0)

def convert_crime_witnessed(answer):
    return 5 if answer == 'Yes' else 0

def convert_police_presence(answer):
    return 5 if answer == 'Yes' else 0

def convert_traffic_signs(answer):
    return 5 if answer == 'Yes' else 0

def convert_lighting(lighting):
    mapping = {
        'Poorly Lit': 1,
        'Moderately Lit': 3,
        'Well-lit': 5
    }
    return mapping.get(lighting, 0)

def convert_security_cameras(answer):
    return 5 if answer == 'Yes' else 0

def convert_road_condition(answer):
    return 5 if answer == 'Yes' else 0

def convert_crowd(crowd):
    mapping = {
        'Deserted': 1,
        'Moderately Crowded': 3,
        'Crowded': 5
    }
    return mapping.get(crowd, 0)

def convert_suspicious_activity(answer):
    return 0 if answer == 'Yes' else 5

def convert_homeless_presence(answer):
    return 0 if answer == 'Yes' else 5


@app.route('/')
def index():
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        contact_count = int(request.form['contact_count'])

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        
        for i in range(1, contact_count + 1):
            name = request.form.get(f'contact_name_{i}')
            number = request.form.get(f'contact_number_{i}')
            if name and number:
                contact = EmergencyContact(user_id=user.id, name=name, phone=number)
                db.session.add(contact)

        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect('/home')
        return 'Invalid Credentials'
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('home.html')

@app.route('/show_routes', methods=['POST'])
def show_routes():
    if 'user_id' not in session:
        return redirect('/login')
    source = request.form['source']
    destination = request.form['destination']
    generate_route_map(source, destination)
    return render_template('route_map.html')

@app.route('/generate_map', methods=['POST'])
def map_view():
    source = request.form['source']
    destination = request.form['destination']
    generate_route_map(source, destination)
    return render_template('route_map.html')
@app.route('/get_area_names')
def get_area_names():
    from generate_map import df  
    area_names = df['AREA'].dropna().unique().tolist()
    return jsonify(area_names)

@app.route("/send_sos", methods=["POST"])
def send_sos():
    user_id = session.get("user_id")
    if not user_id:
        return "User not logged in", 403

    user = User.query.get(user_id)
    contacts = EmergencyContact.query.filter_by(user_id=user_id).all()
    numbers = [contact.phone for contact in contacts]

    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")


    location_link = f"https://www.google.com/maps?q={lat},{lon}"
    message = f"🚨 SOS Alert from SafeVoyage!\nYour contact {user.username} needs help immediately!\nLocation: {location_link}"

    send_sos_alert_fast2sms(numbers, message)

    return "SOS alerts sent!"

@app.route('/give_feedback', methods=['GET'])
def give_feedback():
    return render_template('feedback.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    from generate_map import get_coordinates  

    area_name = request.form['area_name']
    lat, lon = get_coordinates(area_name)

    feedback = SafetyFeedback(
        lat=lat,
        lon=lon,
        place=request.form['place'],
        area_name=request.form['area_name'],
        safety_rating=request.form['safety_rating'], 
        recommend_score=request.form['recommend_score'],  
        police_patrol=request.form['police_patrol'],
        crime_witnessed=request.form['crime_witnessed'],
        crime_description=request.form['crime_description'],
        police_presence=request.form['police_presence'],
        road_safety=request.form['road_safety'],
        traffic_issues=request.form['traffic_issues'],
        traffic_signs=request.form['traffic_signs'],
        lighting=request.form['lighting'],
        security_cameras=request.form['security_cameras'],
        road_condition=request.form['road_condition'],
        crowd=request.form['crowd'],
        suspicious_activity=request.form['suspicious_activity'],
        homeless_presence=request.form['homeless_presence']
    )

    db.session.add(feedback)
    db.session.commit()

    return "Feedback submitted successfully!"

@app.route('/view_feedback', methods=['POST', 'GET'])
def view_feedback():
    if request.method == 'POST':
        place = request.form['place']
        area_name = request.form['area_name']
        
        feedback_data = SafetyFeedback.query.filter_by(place=place, area_name=area_name).all()

        if not feedback_data:
            return render_template('view_feedback.html', no_data=True, place=place, area_name=area_name)

        
        totals = {
            'safety_rating': 0,
            'recommend_score': 0,
            'police_patrol': 0,
            'crime_witnessed': 0,
            'police_presence': 0,
            'road_safety': 0,
            'traffic_issues': 0,
            'traffic_signs': 0,
            'lighting': 0,
            'security_cameras': 0,
            'road_condition': 0,
            'crowd': 0,
            'suspicious_activity': 0,
            'homeless_presence': 0
        }

        crime_description_comments = []
        traffic_issues_comments = []
        total_feedback = len(feedback_data)

        for feedback in feedback_data:
            totals['safety_rating'] += convert_safety_rating(feedback.safety_rating)
            totals['recommend_score'] += convert_recommend_score(feedback.recommend_score)
            totals['police_patrol'] += convert_police_patrol(feedback.police_patrol)
            totals['crime_witnessed'] += convert_crime_witnessed(feedback.crime_witnessed)
            totals['police_presence'] += convert_police_presence(feedback.police_presence)
            totals['road_safety'] += int(feedback.road_safety)
            totals['traffic_issues'] += len(feedback.traffic_issues.split(',')) if feedback.traffic_issues else 0
            totals['traffic_signs'] += convert_traffic_signs(feedback.traffic_signs)
            totals['lighting'] += convert_lighting(feedback.lighting)
            totals['security_cameras'] += convert_security_cameras(feedback.security_cameras)
            totals['road_condition'] += convert_road_condition(feedback.road_condition)
            totals['crowd'] += convert_crowd(feedback.crowd)
            totals['suspicious_activity'] += convert_suspicious_activity(feedback.suspicious_activity)
            totals['homeless_presence'] += convert_homeless_presence(feedback.homeless_presence)

            if feedback.crime_description:
                crime_description_comments.append(feedback.crime_description.strip())
            if feedback.traffic_issues:
                traffic_issues_comments.append(feedback.traffic_issues.strip())

        # Calculate average for each
        averages = {key: round(val / total_feedback, 2) for key, val in totals.items()}

        safety_avg_label = (
            "Very Safe" if averages['safety_rating'] >= 4.5 else
            "Safe" if averages['safety_rating'] >= 3.5 else
            "Neutral" if averages['safety_rating'] >= 2.5 else
            "Risky"
        )
        recommend_avg_label = "Yes" if averages['recommend_score'] >= 3 else "No"

        return render_template('view_feedback.html',
                               place=place, area_name=area_name,
                               safety_avg=safety_avg_label,
                               recommend_avg=recommend_avg_label,
                               police_patrol_avg=averages['police_patrol'],
                               crime_witnessed_avg=averages['crime_witnessed'],
                               police_presence_avg=averages['police_presence'],
                               road_safety_avg=averages['road_safety'],
                               traffic_issues_avg=averages['traffic_issues'],
                               traffic_signs_avg=averages['traffic_signs'],
                               lighting_avg=averages['lighting'],
                               security_cameras_avg=averages['security_cameras'],
                               road_condition_avg=averages['road_condition'],
                               crowd_avg=averages['crowd'],
                               suspicious_activity_avg=averages['suspicious_activity'],
                               homeless_presence_avg=averages['homeless_presence'],
                               crime_description_comments=crime_description_comments,
                               traffic_issues_comments=traffic_issues_comments)
    return render_template('view_feedback.html')

if __name__ == '__main__':
    app.run(debug=True)
