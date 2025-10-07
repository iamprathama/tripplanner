
from flask import current_app as app
from app.utils.places import get_city_image, get_location_id, fetch_attractions, fetch_hotels,get_flight_details
from app.models.user import db, User

from app.ai_gemini import generate_trip_plan
from flask import Flask, render_template, session, flash, request, redirect, url_for,Response
import requests
import markdown
from flask import send_file
from fpdf import FPDF
import io
from io import BytesIO

from dotenv import load_dotenv
import os

load_dotenv()
users=[]
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = user.email
            flash('Login Successful', 'success')
            return redirect(url_for('home_page'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


# @app.route('/download-pdf')
# def download_pdf():
#     plan_text = session.get('plan_raw', 'No plan found.')

#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#     pdf.multi_cell(0, 10, plan_text)

#     pdf_output = pdf.output(dest='S').encode('latin1')
#     buffer = BytesIO()
#     buffer.write(pdf_output)
#     buffer.seek(0)

#     return send_file(
#         buffer,
#         as_attachment=True,
#         download_name="trip_plan.pdf",
#         mimetype='application/pdf'
#     )

import io
import unicodedata
from flask import send_file, session
from fpdf import FPDF

def safe_latin1(text):
    """Convert text to latin-1 safe version, replacing unsupported chars."""
    if not isinstance(text, str):
        text = str(text)
    return unicodedata.normalize('NFKD', text).encode('latin-1', 'replace').decode('latin-1')

@app.route('/download-pdf')
def download_pdf():
    # Get info from session
    city = session.get("selected_city", "Unknown City")
    weather = session.get("weather_info", "Weather not available")
    plan_text = session.get("plan_raw", "Trip plan not found.")

    # Sanitize for PDF output
    city = safe_latin1(city)
    weather = safe_latin1(weather)
    plan_text = safe_latin1(plan_text)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, f"City: {city}")
    pdf.multi_cell(0, 10, f"Weather: {weather}\n")
    pdf.multi_cell(0, 10, "Trip Plan:")
    pdf.multi_cell(0, 10, plan_text)

    # Output PDF in memory
    pdf_output = io.BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)

    return send_file(pdf_output, as_attachment=True, download_name="trip_plan.pdf", mimetype='application/pdf')

# @app.route('/download-pdf')
# def download_pdf():
#     plan_text = session.get('plan_raw', 'No plan found.')
#     city = session.get('selected_city', 'Unknown City')
#     weather = session.get('weather', 'Weather not available')
#     image_url = session.get('city_image_url')  # if you're storing it

#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_auto_page_break(auto=True, margin=15)
#     pdf.set_font("Arial", 'B', 16)

#     # Title
#     pdf.cell(0, 10, 'Your Trip Plan', ln=True, align='C')

#     # Add city and weather
#     pdf.set_font("Arial", '', 12)
#     pdf.ln(10)
#     pdf.cell(0, 10, f'City: {city}', ln=True)
#     pdf.cell(0, 10, f'Weather: {weather}', ln=True)
#     pdf.ln(5)

#     # Add the trip plan content (no markdown)
#     pdf.multi_cell(0, 10, plan_text.replace('*', '').replace('**', ''))

#     # Output as PDF in memory
#     pdf_output = pdf.output(dest='S').encode('latin1')
#     return send_file(io.BytesIO(pdf_output), mimetype='application/pdf', download_name='trip_plan.pdf', as_attachment=True)

# Signup page
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
        
            
                flash("Email already exists. Please login.", "danger")
                return redirect(url_for('login'))

        new_user = User(name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please login now.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')
@app.route('/home')
def home_page():
    if 'email' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))
    return render_template('home.html')
def get_weather(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
   
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        return None

    weather = {
        "temp": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"]
    }
    return weather

@app.route('/create-plan', methods=["GET", "POST"])
def create_plan():
    if 'email' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))

    if request.method == "POST":
        destination = request.form.get("destination")
        days = request.form.get("days")
        budget = request.form.get("budget")
        companions = request.form.get("companions")

        weather = get_weather(destination)

        trip = {
            "destination": destination,
            "days": days,
            "budget": budget,
            "companions": companions
        }
        

        return render_template("view_trip.html", trip=trip, weather=weather)

    return render_template('create_plan.html')
@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    destination = request.form.get("destination")
    days = request.form.get("days")         
    budget = request.form.get("budget")
    companions = request.form.get("companions")
    weather = get_weather(destination)
    

    city_image = get_city_image(destination)
 
    plan = generate_trip_plan(destination, days, budget, companions)
    location_id = get_location_id(destination)
    if not location_id:
        flash("Destination not found!", "danger")
        return redirect(url_for('create_plan'))
    
    attractions = fetch_attractions(location_id)
    city_to_airport = {
        "delhi": "VIDP",
        "mumbai": "VABB",
        "bangalore": "VOBL",
        "jaipur": "VIJP"
    }

    

    # Convert to lowercase for matching
    dest = destination.lower()
    source = "delhi"  # Assume user starts from Delhi

    source_airport = city_to_airport.get(source)
    destination_airport = city_to_airport.get(dest)

  

    today = "2025-07-17"  # 

    flights = get_flight_details(source_airport, destination_airport, today)
    

    hotels = fetch_hotels(location_id)
   
    trip = {
        "destination": destination,
        "days": days,
        "budget": budget,
        "companions": companions
    }
    session['plan_raw'] = plan
    session['trip'] = trip
    session['weather'] = weather
    session['city_image'] = city_image 
    # if you use a flight API
    html_plan = markdown.markdown(plan)
      

    return render_template("view_trip.html", trip=trip, weather=weather, plan=html_plan, city_image=city_image, hotels=hotels , places=attractions ,
        flights=flights)



