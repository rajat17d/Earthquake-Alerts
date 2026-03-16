import requests
import math

# --- 1. YOUR OFFICE DATA FROM IMAGE ---
# I have mapped your specific coordinates and details here
OFFICES = [
    {"state": "ANDHRA PRADESH", "site": "Vijaywada", "prop": "RENTED", "lat": 16.54228, "lon": 80.79144, "capacity": 165},
    {"state": "TELANGANA", "site": "DC Kompally", "prop": "RENTED", "lat": 17.55942136, "lon": 78.50374708, "capacity": 80},
    {"state": "ASSAM", "site": "Guwahati", "prop": "RENTED", "lat": 26.204444, "lon": 91.68025, "capacity": 208},
    {"state": "BIHAR", "site": "Patna", "prop": "RENTED", "lat": 25.58110392, "lon": 85.10967193, "capacity": 243},
    {"state": "JHARKHAND", "site": "Ranchi", "prop": "RENTED", "lat": 23.307238, "lon": 85.398365, "capacity": 225},
    {"state": "DELHI", "site": "Delhi", "prop": "RENTED", "lat": 28.815834, "lon": 77.14023, "capacity": 270},
    {"state": "DELHI", "site": "Noida DC", "prop": "RENTED", "lat": 28.53467, "lon": 77.44672, "capacity": 0},
    {"state": "GUJARAT", "site": "Ahmedabad", "prop": "RENTED", "lat": 22.8998011, "lon": 72.59049147, "capacity": 72},
    {"state": "GUJARAT", "site": "Surat", "prop": "OWNED", "lat": 21.14953001, "lon": 72.77377413, "capacity": 120},
    {"state": "HIMACHAL PRADESH", "site": "Parwanoo", "prop": "RENTED", "lat": 30.83680891, "lon": 76.96602879, "capacity": 180},
    {"state": "HARYANA", "site": "Farrukhnagar", "prop": "RENTED", "lat": 28.37775974, "run": 76.83093171, "capacity": 54},
    {"state": "HARYANA", "site": "RRL SDC HR Gurgaon New1", "prop": "RENTED", "lat": 28.43593011, "lon": 76.65597871, "capacity": 225}
]

# --- 2. ALERT SETTINGS ---
ALERT_RADIUS_KM = 150  # Notify if quake is within 150km of office
MIN_MAGNITUDE = 4.0    # Only notify for magnitude 4.0 or higher
SLACK_WEBHOOK_URL = "PASTE_YOUR_WEBHOOK_URL_HERE" # We'll set this next

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def send_notification(office, mag, dist, place):
    # Formats the alert exactly as you requested
    alert_text = (
        f"🚨 *EARTHQUAKE ALERT* 🚨\n"
        f"*Magnitude:* {mag} | *Location:* {place}\n"
        f"----------------------------------\n"
        f"📍 *Affected Site:* {office['site']}\n"
        f"🌎 *State:* {office['state']}\n"
        f"🏠 *Property Type:* {office['prop']}\n"
        f"👥 *Seating Capacity (Employees at Risk):* {office['capacity']}\n"
        f"📏 *Distance from Office:* {dist:.1f} km"
    )
    
    print(alert_text) # This shows in GitHub logs
    
    # If you have a webhook, this sends it to Slack/Teams
    if "http" in SLACK_WEBHOOK_URL:
        requests.post(SLACK_WEBHOOK_URL, json={"text": alert_text})

def check_quakes():
    # USGS "Past Hour" Feed
    url = "https://earthquake.usgs.gov"
    try:
        data = requests.get(url).json()
    except:
        return

    for event in data['features']:
        mag = event['properties']['mag']
        place = event['properties']['place']
        # USGS coordinates are [longitude, latitude]
        eq_lon = event['geometry']['coordinates'][0]
        eq_lat = event['geometry']['coordinates'][1]

        for office in OFFICES:
            dist = haversine(office['lat'], office['lon'], eq_lat, eq_lon)
            if dist <= ALERT_RADIUS_KM and mag >= MIN_MAGNITUDE:
                send_notification(office, mag, dist, place)

if __name__ == "__main__":
    check_quakes()
