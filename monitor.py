import requests
import math

# --- 1. YOUR CONNECTOR CONFIGURATION ---
TEAMS_WEBHOOK_URL = "https://rilcloud.webhook.office.com/webhookb2/8afc6530-cf1c-4355-9a99-5867d84e87b0@fe1d95a9-4ce1-41a5-8eab-6dd43aa26d9f/IncomingWebhook/500056a107ac4d02ba1463c798ef4372/8726cf75-4eee-40ac-8179-e36f286fbba6/V2pKR-d1Pmg2FH0fGKG0lOrAKjrGUEwlwYij0bhzREdok1"

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
    {"state": "HARYANA", "site": "Farrukhnagar", "prop": "RENTED", "lat": 28.37775974, "lon": 76.83093171, "capacity": 54},
    {"state": "HARYANA", "site": "RRL SDC HR Gurgaon New1", "prop": "RENTED", "lat": 28.43593011, "lon": 76.65597871, "capacity": 225}
]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def send_teams_alert(office, mag, dist, place):
    # Payload format for Office 365 Incoming Webhook Connector
    payload = {
        "summary": "Enterprise Earthquake Alert",
        "themeColor": "FF0000",
        "sections": [{
            "activityTitle": "⚠️ EARTHQUAKE ALERT DETECTED",
            "activitySubtitle": f"Epicenter: {place}",
            "facts": [
                {"name": "State:", "value": office['state']},
                {"name": "Site Office:", "value": office['site']},
                {"name": "Property Type:", "value": office['prop']},
                {"name": "Seating Capacity:", "value": str(office['capacity'])},
                {"name": "Magnitude:", "value": str(mag)},
                {"name": "Distance to Office:", "value": f"{dist:.1f} km"}
            ],
            "markdown": True
        }]
    }
    response = requests.post(TEAMS_WEBHOOK_URL, json=payload)
    print(f"Teams Response for {office['site']}: {response.status_code}")

def check_quakes():
    url = "https://earthquake.usgs.gov"
    try:
        data = requests.get(url).json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    for event in data.get('features', []):
        mag = event['properties'].get('mag')
        place = event['properties'].get('place')
        coords = event['geometry']['coordinates'] # [longitude, latitude]
        
        # Test Filters (Currently set to GLOBAL for testing)
        for office in OFFICES:
            dist = haversine(office['lat'], office['lon'], coords[1], coords[0])
            
            # --- START TESTING LOGIC ---
            # Change dist to <= 250 and mag to >= 4.0 after your test works
            if dist <= 20000 and mag and mag >= 0.1:
                send_teams_alert(office, mag, dist, place)
                return # Only sends ONE alert for the test to avoid spam
            # --- END TESTING LOGIC ---

if __name__ == "__main__":
    check_quakes()
