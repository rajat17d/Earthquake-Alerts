import requests
import math

# --- 1. FIXED OFFICE DATA ---
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
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def check_quakes():
    url = "https://earthquake.usgs.gov"
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    for event in data.get('features', []):
        mag = event['properties'].get('mag')
        place = event['properties'].get('place')
        coords = event['geometry']['coordinates']
        
        # USGS format is [longitude, latitude, depth]
        eq_lon = coords[0]
        eq_lat = coords[1]

        if mag is None: continue

        for office in OFFICES:
            dist = haversine(office['lat'], office['lon'], eq_lat, eq_lon)
            # Logic: Mag > 4.0 and within 200km
            if dist <= 200 and mag >= 4.0:
                print(f"!!! MATCH !!! {mag} mag near {office['site']}, {office['state']}")
                # We will add the notification send part once this runs successfully

if __name__ == "__main__":
    check_quakes()
