import requests
import math

# --- 1. CONFIGURATION ---
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
    # This matches the "Adaptive Card" requirement of your Power Automate flow
    payload = {
        "type": "message",
        "attachments":},
                        {"name": "Site Office:", "value": office['site']},
                        {"title": "Property:", "value": office['prop']},
                        {"title": "Capacity:", "value": str(office['capacity'])},
                        {"title": "Magnitude:", "value": str(mag)},
                        {"title": "Distance:", "value": f"{dist:.1f} km"},
                        {"title": "Location:", "value": place}
                    ]}
                ],
                "$schema": "http://adaptivecards.io",
                "version": "1.4"
            }
        }]
    }
    r = requests.post(TEAMS_WORKFLOW_URL, json=payload)
    print(f"Workflow Status: {r.status_code}")

def check_quakes():
    # TEST: Using past day to guarantee we find a sample quake for your first alert
    url = "https://earthquake.usgs.gov"
    data = requests.get(url).json()
    
    for event in data.get('features', []):
        mag = event['properties'].get('mag')
        place = event['properties'].get('place')
        lon, lat, depth = event['geometry']['coordinates']

        for office in OFFICES:
            dist = haversine(office['lat'], office['lon'], lat, lon)
            # TEST MODE: 20000km so it triggers immediately
            if dist <= 20000 and mag and mag >= 0.1:
                send_alert(office, mag, dist, place)
                return # Stop after sending the test alert

if __name__ == "__main__":
    check_quakes()
