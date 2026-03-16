import requests
import math

# --- CONFIGURATION ---
TEAMS_WEBHOOK_URL = "https://rilcloud.webhook.office.com/webhookb2/8afc6530-cf1c-4355-9a99-5867d84e87b0@fe1d95a9-4ce1-41a5-8eab-6dd43aa26d9f/IncomingWebhook/500056a107ac4d02ba1463c798ef4372/8726cf75-4eee-40ac-8179-e36f286fbba6/V2pKR-d1Pmg2FH0fGKG0lOrAKjrGUEwlwYij0bhzREdok1"

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def send_alert(mag, place):
    payload = {"text": f"✅ CONNECTION TEST\nEarthquake: Mag {mag} at {place}"}
    try:
        r = requests.post(TEAMS_WEBHOOK_URL, json=payload, timeout=10)
        print(f"Teams Response: {r.status_code}")
    except Exception as e:
        print(f"Failed to send to Teams: {e}")

def check_quakes():
    url = "https://earthquake.usgs.gov"
    try:
        response = requests.get(url, timeout=15)
        # Check if the response is actually valid JSON
        if response.status_code != 200:
            print(f"USGS API Error: Status {response.status_code}")
            return
        
        data = response.json()
        
        if 'features' in data and len(data['features']) > 0:
            # Grab the latest quake for the test
            first = data['features'][0]
            mag = first['properties']['mag']
            place = first['properties']['place']
            print(f"Found quake: {place} (Mag: {mag})")
            send_alert(mag, place)
        else:
            print("No earthquakes found in the feed.")

    except requests.exceptions.JSONDecodeError:
        print("Error: Received invalid JSON from USGS (could be a rate limit).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    check_quakes()
