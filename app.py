from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["flight_reservation"]
users_collection = db["users"]
flights_collection = db["flights"]
reservations_collection = db["reservations"]

# Dummy flights data
sample_flights = [
    {"flight_no": "AI101", "source": "Delhi", "destination": "Mumbai", "date": "2025-04-24", "time": "10:00 AM"},
    {"flight_no": "AI102", "source": "Delhi", "destination": "Bangalore", "date": "2025-04-23", "time": "02:00 PM"},
    {"flight_no": "AI103", "source": "Mumbai", "destination": "Delhi", "date": "2025-04-23", "time": "11:30 AM"},
    {"flight_no": "AI104", "source": "Chennai", "destination": "Delhi", "date": "2025-04-23", "time": "05:00 PM"},
    {"flight_no": "AI105", "source": "Delhi", "destination": "Hyderabad", "date": "2025-04-24", "time": "08:00 AM"},
]

# Insert sample flights once
if flights_collection.count_documents({}) == 0:
    flights_collection.insert_many(sample_flights)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    role = request.form['role']
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard', username=username))

@app.route('/user/<username>')
def user_dashboard(username):
    return render_template('user_dashboard.html', username=username)

@app.route('/search_flights', methods=['POST'])
def search_flights():
    source = request.form['source'].strip().title()
    destination = request.form['destination'].strip().title()
    date = request.form['date'].strip()
    trip_type = request.form['trip_type']
    return_date = request.form.get('return_date', '')
    username = request.form['username']

    # Try matching exactly in DB
    flights = list(flights_collection.find({
        "source": source,
        "destination": destination,
        "date": date
    }))

    return render_template(
        'flight_results.html',
        flights=flights,
        source=source,
        destination=destination,
        date=date,
        trip_type=trip_type,
        return_date=return_date,
        username=username
    )


@app.route('/book_flight', methods=['POST'])
def book_flight():
    flight_no = request.form['flight_no']
    username = request.form['username']
    trip_type = request.form['trip_type']
    return_date = request.form.get('return_date', '')

    flight = flights_collection.find_one({"flight_no": flight_no})
    reservation = {
        "username": username,
        "flight_no": flight_no,
        "trip_type": trip_type,
        "source": flight['source'],
        "destination": flight['destination'],
        "departure_date": flight['date'],
        "return_date": return_date if trip_type == 'round' else '',
        "time": flight['time'],
        "booking_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    reservations_collection.insert_one(reservation)
    return render_template('confirmation.html', reservation=reservation)

@app.route('/admin')
def admin_dashboard():
    reservations = list(reservations_collection.find())
    return render_template('admin_dashboard.html', reservations=reservations)

if __name__ == '__main__':
    app.run(debug=True)