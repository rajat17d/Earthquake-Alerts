import requests
import math

# --- 1. FULL TEAMS WORKFLOW URL ---
TEAMS_WORKFLOW_URL = "https://defaultfe1d95a94ce141a58eab6dd43aa26d.9f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/c2bbf7a14d584876a3b81a8a7fbedbac/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=20YX9Mf323evgcxN68y6fdUcQWBdLxbtuEUJsnP1bcU"

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

def send_alert(office, mag, dist, place):
    # This format is required for Power Automate Workflows
    payload = {"text": f"⚠️ EARTHQUAKE ALERT\n\nSite: {office['site']} ({office['state']})\nMagnitude: {mag}\nDistance: {dist:.1f} km\nEpicenter: {place}"}
    try:
        r = requests.post(TEAMS_WORKFLOW_URL, json=payload, timeout=10)
        print(f"Teams Status: {r.status_code}")
    except Exception as e:
        print(f"Teams Error: {e}")

def check_quakes():
    url = "https://earthquake.usgs.gov"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200: return
        data = response.json()
        
        for event in data.get('features', []):
            mag = event['properties'].get('mag')
            place = event['properties'].get('place')
            coords = event['geometry']['coordinates'] # [longitude, latitude, depth]
            
            # --- FIX: Extract Lat and Lon correctly from USGS list ---
            eq_lon = coords[0]
            eq_lat = coords[1]

            for office in OFFICES:
                dist = haversine(office['lat'], office['lon'], eq_lat, eq_lon)
                # FORCED TEST: Set dist to 20000 and mag to 0.1 for the FIRST RUN
                if dist <= 20000 and mag and mag >= 0.1:
                    send_alert(office, mag, dist, place)
                    return # Send just one for the test
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_quakes()
