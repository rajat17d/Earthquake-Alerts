import requests
import math
import sys

# --- 1. CONFIGURATION ---
URL = "https://defaultfe1d95a94ce141a58eab6dd43aa26d.9f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/c2bbf7a14d584876a3b81a8a7fbedbac/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=20YX9Mf323evgcxN68y6fdUcQWBdLxbtuEUJsnP1bcU"

OFFICES = [
    {"state": "ANDHRA PRADESH",   "site": "Vijaywada",      "lat": 16.54228,  "lon": 80.79144,  "capacity": 165},
    {"state": "TELANGANA",        "site": "DC Kompally",    "lat": 17.559421, "lon": 78.503747, "capacity": 80},
    {"state": "ASSAM",            "site": "Guwahati",       "lat": 26.204444, "lon": 91.68025,  "capacity": 208},
    {"state": "BIHAR",            "site": "Patna",          "lat": 25.581103, "lon": 85.109671, "capacity": 243},
    {"state": "JHARKHAND",        "site": "Ranchi",         "lat": 23.307238, "lon": 85.398365, "capacity": 225},
    {"state": "DELHI",            "site": "Delhi",          "lat": 28.815834, "lon": 77.14023,  "capacity": 270},
    {"state": "GUJARAT",          "site": "Ahmedabad",      "lat": 22.899801, "lon": 72.590491, "capacity": 72},
    {"state": "GUJARAT",          "site": "Surat",          "lat": 21.14953,  "lon": 72.773774, "capacity": 120},
    {"state": "HIMACHAL PRADESH", "site": "Parwanoo",       "lat": 30.836808, "lon": 76.966028, "capacity": 180},
    {"state": "HARYANA",          "site": "Farrukhnagar",   "lat": 28.377759, "lon": 76.830931, "capacity": 54}
]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return 2 * R * math.asin(math.sqrt(a))

def send_alert(office, mag, dist, place):
    payload = {
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "State:",     "value": office['state']},
                                {"title": "Magnitude:", "value": str(mag)},
                                {"title": "Distance:",  "value": str(round(dist, 1)) + " km"},
                                {"title": "Location:",  "value": str(place)},
                                {"title": "Capacity:",  "value": str(office['capacity'])}
                            ]
                        }
                    ],
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
                }
            }
        ]
    }
    r = requests.post(URL, json=payload, timeout=10)
    print(f"Alert sent to {office['site']} — Status Code: {r.status_code}")

def main():
    api_url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=100&minmagnitude=0.1"
    try:
        response = requests.get(api_url, timeout=15)
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
                if dist <= 1000 and mag and mag >= 0.1:
                    send_alert(office, mag, dist, place)

                    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
