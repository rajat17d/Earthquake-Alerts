import math
import sys
import json

# Try to import requests
try:
    import requests
except ImportError:
    print("ERROR: 'requests' library is not installed. Ensure requirements.txt exists with 'requests' inside.")
    sys.exit(1)

# --- 1. CONFIGURATION ---
URL = "https://defaultfe1d95a94ce141a58eab6dd43aa26d.9f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/c2bbf7a14d584876a3b81a8a7fbedbac/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=20YX9Mf323evgcxN68y6fdUcQWBdLxbtuEUJsnP1bcU"

OFFICES = [
    {"state": "ANDHRA PRADESH", "site": "Vijaywada", "lat": 16.54228, "lon": 80.79144, "capacity": 165},
    {"state": "TELANGANA", "site": "DC Kompally", "lat": 17.55942136, "lon": 78.50374708, "capacity": 80},
    {"state": "ASSAM", "site": "Guwahati", "lat": 26.204444, "lon": 91.68025, "capacity": 208},
    {"state": "BIHAR", "site": "Patna", "lat": 25.58110392, "lon": 85.10967193, "capacity": 243},
    {"state": "JHARKHAND", "site": "Ranchi", "lat": 23.307238, "lon": 85.398365, "capacity": 225},
    {"state": "DELHI", "site": "Delhi", "lat": 28.815834, "lon": 77.14023, "capacity": 270},
    {"state": "GUJARAT", "site": "Ahmedabad", "lat": 22.8998011, "lon": 72.59049147, "capacity": 72},
    {"state": "GUJARAT", "site": "Surat", "lat": 21.14953001, "lon": 72.77377413, "capacity": 120},
    {"state": "HIMACHAL PRADESH", "site": "Parwanoo", "lat": 30.83680891, "lon": 76.96602879, "capacity": 180},
    {"state": "HARYANA", "site": "Farrukhnagar", "lat": 28.37775974, "lon": 76.83093171, "capacity": 54}
]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def send_alert(office, mag, dist, place):
    # This structure is specifically for the "Initialize variable (Attachments)" step in your Flow
    payload = {
        "attachments":} ({office['state']})"},
                            {"title": "Magnitude:", "value": str(mag)},
                            {"title": "Distance:", "value": f"{dist:.1f} km"},
                            {"title": "Location:", "value": str(place)},
                            {"title": "Risk Capacity:", "value": str(office['capacity'])}
                        ]}
                    ],
                    "$schema": "http://adaptivecards.io"
                }
            }
        ]
    }
    r = requests.post(URL, json=payload)
    print(f"Teams Status: {r.status_code}")

def main():
    print("Checking USGS earthquake feed...")
    try:
        # Fetching past 24 hours of data to guarantee a test alert
        response = requests.get("https://earthquake.usgs.gov", timeout=20)
        data = response.json()
        
        for event in data.get('features', []):
            mag = event['properties'].get('mag')
            place = event['properties'].get('place')
            coords = event['geometry'].get('coordinates')

            if not coords or len(coords) < 2:
                continue

            eq_lon = coords[0]
            eq_lat = coords[1]

            for office in OFFICES:
                dist = haversine(office['lat'], office['lon'], eq_lat, eq_lon)
                
                # --- TEST MODE --- 
                # (Triggers for ANY global quake in last 24h to verify your Teams connection)
                if dist <= 20000 and mag and mag >= 0.1:
                    print(f"Match found! Sending card for {office['site']}...")
                    send_alert(office, mag, dist, place)
                    return 
                    
        print("Done. No matching earthquakes found.")
    except Exception as e:
        print(f"Script Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
