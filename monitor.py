import requests
import math

# --- 1. FULL CONNECTOR URL ---
TEAMS_WEBHOOK_URL = "https://rilcloud.webhook.office.com/webhookb2/8afc6530-cf1c-4355-9a99-5867d84e87b0@fe1d95a9-4ce1-41a5-8eab-6dd43aa26d9f/IncomingWebhook/500056a107ac4d02ba1463c798ef4372/8726cf75-4eee-40ac-8179-e36f286fbba6/V2pKR-d1Pmg2FH0fGKG0lOrAKjrGUEwlwYij0bhzREdok1"

OFFICE = {"state": "DELHI", "site": "TEST OFFICE", "prop": "RENTED", "lat": 28.815, "lon": 77.140, "capacity": 100}

def send_test_alert(mag, place):
    # Simplest possible format for Enterprise Teams
    payload = {
        "text": f"✅ **CONNECTION SUCCESSFUL**\n\nEarthquake detected: Mag {mag} at {place}.\nYour GitHub-to-Teams alert system is now active!"
    }
    r = requests.post(TEAMS_WEBHOOK_URL, json=payload)
    print(f"Teams Response: {r.status_code}")

def check_quakes():
    # TEST: Using 'past day' feed to ensure we find an earthquake
    url = "https://earthquake.usgs.gov"
    data = requests.get(url).json()
    
    # Grab just the very first earthquake in the list to test the connection
    if data['features']:
        first_quake = data['features'][0]
        mag = first_quake['properties']['mag']
        place = first_quake['properties']['place']
        
        print(f"Testing connection with quake at: {place}")
        send_test_alert(mag, place)
    else:
        print("No earthquakes found in USGS feed.")

if __name__ == "__main__":
    check_quakes()
