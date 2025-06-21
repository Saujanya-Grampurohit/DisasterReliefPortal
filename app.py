from flask import Flask, render_template, request, redirect
from datetime import datetime
import os
import json
from collections import defaultdict
from flask import jsonify
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure Flask-Mail (add these once at the top after app = Flask(__name__))
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'saujanya.grampurohit@cumminscollege.in'         # Replace
app.config['MAIL_PASSWORD'] = 'jwbienpjzvxwuezb'      # Replace

mail = Mail(app)


# ------------------------------
# Coordinate map for cities
# ------------------------------
location_coords = {
    "pune": [18.5204, 73.8567],
    "mumbai": [19.0760, 72.8777],
    "nagpur": [21.1458, 79.0882],
    "nashik": [19.9975, 73.7898],
    "chandrapur": [19.9615, 79.2961],
    "thane": [19.2183, 72.9781],
    "raigad": [18.5158, 73.1800],
    "wayanad": [11.6850, 76.1310],
    "ratnagiri": [16.9902, 73.3120],
    "sangli": [16.8524, 74.5815],
    "palghar": [19.6964, 72.7652],
    "satara": [17.6805, 74.0183]
}

# ------------------------------
# Sample data for shelters
# ------------------------------
mock_data = {
    "pune": {
        "nearby": ["Lonavla", "Chakan", "Shikrapur"],
        "farby": ["Satara", "Ratnagiri", "Wayanad"],
        "shelters": ["Spherule Foundation", "Wings for Dreams", "Sanjivsni NGO"]
    },
    "mumbai": {
        "nearby": ["Thane", "Navi Mumbai", "Karjat"],
        "farby": ["Palghar", "Raigad", "Chandrapur"],
        "shelters": ["Red Cross Shelter", "Disaster Center A", "NGO Ground Unit"]
    },
    "nagpur": {
        "nearby": ["Wardha", "Amravati", "Bhandara"],
        "farby": ["Yavatmal", "Washim", "Gondia"],
        "shelters": ["Unity Hall", "Community Rescue Center", "Medical Camp Nagpur"]
    },
    "nashik": {
        "nearby": ["Sinnar", "Igatpuri", "Trimbak"],
        "farby": ["Dhule", "Malegaon", "Ahmednagar"],
        "shelters": ["Shelter Trust Nashik", "Helping Hands", "ZP School Shelter"]
    },
    "satara": {
        "nearby": ["Karad", "Patan", "Mahabaleshwar"],
        "farby": ["Kolhapur", "Sangli", "Solapur"],
        "shelters": ["Relief Center Satara", "Disaster Shelter South", "Temple Community Hall"]
    },
    "raigad": {
        "nearby": ["Pen", "Panvel", "Uran"],
        "farby": ["Alibag", "Shrivardhan", "Mahad"],
        "shelters": ["Coastal Rescue Unit", "Civic Shelter A", "Mission Relief"]
    }
}

# ------------------------------
# NGO Locations by City
# ------------------------------
ngo_locations = {
    "pune": [18.5289, 73.8470],         # Spherule Foundation
    "mumbai": [19.0640, 72.8777],       # Red Cross Mumbai
    "nashik": [19.9830, 73.7740],       # Samagra Foundation
    "nagpur": [21.1458, 79.0882],
    "chandrapur": [19.9615, 79.2961],
    "thane": [19.2183, 72.9781],
    "raigad": [18.5158, 73.1800],
    "wayanad": [11.6850, 76.1310],
    "ratnagiri": [16.9902, 73.3120],
    "sangli": [16.8524, 74.5815],
    "palghar": [19.6964, 72.7652],
    "satara": [17.6805, 74.0183]
}


# ------------------------------
# Routes
# ------------------------------

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/victim')
def victim():
    return render_template("victim.html")

@app.route('/victim-report', methods=['POST'])
def handle_victim():
    area = request.form['area'].lower()
    disaster_type = request.form['type'].strip().lower()
    print("Disaster Type Received:", disaster_type)
    source = request.form['source'].strip().lower()
    dest = request.form['destination'].strip().lower()

    print("Source City:", source)
    print("Destination City:", dest)


    van_requested_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    estimated_arrival = 20

    base_info = mock_data.get(area, {
        "nearby": ["Unknown"],
        "farby": ["Unknown"],
        "shelters": ["Unknown"]
    })

    # Conditional selection of area type
    if disaster_type in ["flood", "earthquake"]:
        selected_areas = base_info["farby"]
        area_type = "Farby Areas"
    else:
        selected_areas = base_info["nearby"]
        area_type = "Nearby Areas"

    ngo_coords = ngo_locations.get(area, [0, 0])
    src_coords = location_coords.get(source.strip().lower(), [0, 0])
    dest_coords = location_coords.get(dest.strip().lower(), [0, 0])



    # ✅ Move print OUTSIDE render_template
    print("SOURCE COORDINATES:", src_coords)
    print("DESTINATION COORDINATES:", dest_coords)
    if src_coords == [0, 0] or dest_coords == [0, 0]:
        print("⚠️ WARNING: Invalid source or destination name entered!")


    return render_template("results.html",
        area=area,
        disaster_type=disaster_type,
        van_time=estimated_arrival,
        van_requested_time=van_requested_time,

        src_coords=src_coords,
        dest_coords=dest_coords,
        ngo_coords=ngo_coords,


        info=base_info,
        area_type=area_type,
        selected_areas=selected_areas,
        path=[source.title(), "Checkpoint A", "Checkpoint B", dest.title()]
    )


# ------------------------------
# Optional Volunteers Route (If Needed)
# ------------------------------

VOLUNTEER_FILE = 'data/volunteers.txt'
FUND_FILE = 'data/funds.txt'

def save_volunteer(data):
    os.makedirs("data", exist_ok=True)
    with open(VOLUNTEER_FILE, "a") as f:
        f.write(";".join(data.values()) + "\n")

def load_volunteers():
    volunteers = []
    if os.path.exists(VOLUNTEER_FILE):
        with open(VOLUNTEER_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(";")
                if len(parts) >= 6:
                    volunteers.append({
                        "name": parts[0],
                        "phone": parts[1],
                        "address": parts[2],
                        "city": parts[3],
                        "aidType": parts[4],
                        "amount": float(parts[5]) if parts[4] == "money" else 0.0
                    })
    return volunteers

def save_funds(amount):
    current = 0
    if os.path.exists(FUND_FILE):
        with open(FUND_FILE) as f:
            current = float(f.read().strip())
    current += float(amount)
    with open(FUND_FILE, "w") as f:
        f.write(str(current))

def get_total_funds():
    if os.path.exists(FUND_FILE):
        with open(FUND_FILE) as f:
            return float(f.read().strip())
    return 0

@app.route('/volunteer')
def volunteer():
    return render_template("volunteer.html")

@app.route('/register-volunteer', methods=['POST'])
def register_volunteer():
    form = request.form
    data = {
        "name": form['name'],
        "phone": form['phone'],
        "address": form['address'],
        "city": form['city'].lower(),
        "aidType": form['aidType'],
        "amount": form.get('amount') or '0'
    }
    save_volunteer(data)
    if data['aidType'] == 'money':
        save_funds(data['amount'])

    # ✅ Add this block to send an email after successful registration
    msg = Message("🤝 Volunteer Registered",
    sender="your_email@gmail.com",
    recipients=["your_email@gmail.com"])  # or admin email

    msg.body = f"""
New volunteer has registered:

Name: {data['name']}
Phone: {data['phone']}
City: {data['city'].title()}
Type of Aid: {data['aidType']}
Amount (if money): {data['amount']}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

    try:
        mail.send(msg)
        print("📧 Volunteer registration email sent.")
    except Exception as e:
        print("❌ Failed to send volunteer email:", e)

    return redirect("/volunteers")

@app.route('/volunteers')
def show_volunteers():
    volunteers = load_volunteers()
    aid_count = defaultdict(int)
    city_map = defaultdict(list)

    unique_set = set()  # to track unique volunteers

    for v in volunteers:
        # Define uniqueness by name + city + aid type + amount
        key = (v['name'].strip().lower(),
                v['city'].strip().lower(),
                v['aidType'].strip().lower(),
                float(v['amount']))

        if key not in unique_set:
            unique_set.add(key)
            aid_count[v['aidType']] += 1
            city_map[v['city'].title()].append(v)

    chart_data = json.dumps(aid_count)
    return render_template("volunteers.html",
        volunteers=volunteers,
        cities=city_map,
        chart=chart_data,
        total=get_total_funds())


@app.route('/sos-alert', methods=['POST'])
def sos_alert():
    data = request.get_json()
    phone = data.get('phone', 'Unknown')
    area = data.get('area', 'Unknown')

    msg = Message("🆘 Emergency SOS Alert",
    sender="your_email@gmail.com",
    recipients=["rescue_team@example.com"])  # Replace with rescue team email

    msg.body = f"""
🚨 SOS Triggered!

Victim Phone: {phone}
Location: {area}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
    """

    try:
        mail.send(msg)
        print("📧 SOS email sent.")
        return '', 204
    except Exception as e:
        print("❌ Failed to send SOS email:", e)
        return jsonify({'error': str(e)}), 500

# ------------------------------
# Run the Flask App
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
