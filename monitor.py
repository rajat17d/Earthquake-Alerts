import requests
import math
import sys
import os
import io
import json
import pandas as pd
from datetime import datetime, timezone

# --- 1. CONFIGURATION ---
URL     = os.environ["POWERAUTOMATE_URL"]
PAT     = os.environ["DATA_PAT"]
csv_url = "https://raw.githubusercontent.com/rajat17d/earthquake-monitor/main/offices.csv"

# Alert thresholds
TIER1_MAG = 6.0;  TIER1_DIST = 300
TIER2_MAG = 5.0;  TIER2_DIST = 200
TIER2_FAR_MAG = 6.0; TIER2_FAR_DIST_MIN = 300; TIER2_FAR_DIST_MAX = 500

SEEN_IDS_FILE = "seen_events.json"

def load_seen_ids():
    try:
        with open(SEEN_IDS_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_seen_ids(ids):
    with open(SEEN_IDS_FILE, "w") as f:
        json.dump(list(ids), f)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def get_tier(mag, dist, depth):
    depth_label = "Shallow" if depth < 70 else ("Intermediate" if depth < 300 else "Deep")
    if mag >= TIER1_MAG and dist <= TIER1_DIST:
        return 1, "HIGH ALERT", "attention", depth_label
    if (mag >= TIER2_MAG and dist <= TIER2_DIST) or \
       (mag >= TIER2_FAR_MAG and TIER2_FAR_DIST_MIN < dist <= TIER2_FAR_DIST_MAX):
        return 2, "WATCH ALERT", "warning", depth_label
    return None, None, None, depth_label

def send_combined_alert(tier1_matches, tier2_matches):
    timestamp = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    total     = len(tier1_matches) + len(tier2_matches)

    def make_rows(matches, row_style):
        rows = []
        for m in matches:
            rows.append({
                "type": "TableRow",
                "style": row_style,
                "cells": [
                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": m["state"],                             "wrap": True}]},
                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": m["tier_label"],                        "wrap": True}]},
                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": str(m["mag"]),                          "wrap": True, "horizontalAlignment": "Center"}]},
                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": f"{round(m['dist'],1)} km",             "wrap": True, "horizontalAlignment": "Center"}]},
                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": m["place"],                             "wrap": True}]},
                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": f"{m['depth_type']} ({m['depth']} km)", "wrap": True}]},
                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": str(m["capacity"]),                     "wrap": True, "horizontalAlignment": "Center"}]}
                ]
            })
        return rows

    all_rows = make_rows(tier1_matches, "attention") + make_rows(tier2_matches, "warning")

    payload = {
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.5",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "Earthquake Alert - Offices Within Risk Zone",
                        "weight": "Bolder", "size": "Large", "color": "Attention", "wrap": True
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                            {"type": "Column", "width": "stretch",
                             "items": [{"type": "TextBlock",
                                        "text": f"HIGH ALERT (Mag 6.0+, 300km): {len(tier1_matches)} | WATCH (Mag 5.0+, 200km): {len(tier2_matches)}",
                                        "isSubtle": True, "wrap": True}]},
                            {"type": "Column", "width": "auto",
                             "items": [{"type": "TextBlock",
                                        "text": f"Updated: {timestamp}",
                                        "isSubtle": True, "horizontalAlignment": "Right"}]}
                        ]
                    },
                    {
                        "type": "Table",
                        "gridStyle": "accent",
                        "firstRowAsHeaders": True,
                        "columns": [{"width": 2}, {"width": 2}, {"width": 1}, {"width": 1}, {"width": 3}, {"width": 2}, {"width": 1}],
                        "rows": [
                            {
                                "type": "TableRow", "style": "accent",
                                "cells": [
                                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": "State",               "weight": "Bolder"}]},
                                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": "Alert Level",         "weight": "Bolder"}]},
                                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": "Magnitude",           "weight": "Bolder", "horizontalAlignment": "Center"}]},
                                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": "Distance",            "weight": "Bolder", "horizontalAlignment": "Center"}]},
                                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": "Earthquake Location", "weight": "Bolder"}]},
                                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": "Depth",               "weight": "Bolder"}]},
                                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": "Capacity",            "weight": "Bolder", "horizontalAlignment": "Center"}]}
                                ]
                            },
                            *all_rows
                        ]
                    }
                ]
            }
        }]
    }

    r = requests.post(URL, json=payload, timeout=10)
    print(f"Alert sent — {total} match(es) | Status: {r.status_code}")

def main():
    seen_ids = load_seen_ids()
    new_ids  = set()

    try:
        # Load offices from private repo
        resp = requests.get(csv_url, headers={"Authorization": f"token {PAT}"}, timeout=10)
        if resp.status_code != 200:
            print(f"Failed to fetch offices.csv — Status: {resp.status_code}")
            sys.exit(1)
        OFFICES = pd.read_csv(io.StringIO(resp.text)).to_dict(orient="records")
        print(f"Offices loaded: {len(OFFICES)}")

        # Fetch USGS data
        api_url  = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=20&minmagnitude=4.8&orderby=time"
        print("Fetching earthquake data from USGS...")
        response = requests.get(api_url, timeout=15)
        data     = response.json()
        features = data.get("features", [])
        print(f"Total earthquakes fetched: {len(features)}")

        tier1_matches, tier2_matches = [], []

        for event in features:
            event_id = event.get("id")
            if event_id in seen_ids:
                print(f"  Skipping already alerted: {event_id}")
                continue

            mag    = event["properties"].get("mag")
            place  = event["properties"].get("place")
            coords = event["geometry"].get("coordinates")
            if not coords or len(coords) < 3 or not mag:
                continue

            eq_lon, eq_lat, eq_depth = coords[0], coords[1], coords[2]

            for office in OFFICES:
                dist = haversine(float(office["lat"]), float(office["lon"]), eq_lat, eq_lon)
                tier, tier_label, row_style, depth_label = get_tier(mag, dist, eq_depth)

                if tier:
                    print(f"  {'T1' if tier==1 else 'T2'} {office['state']} | Mag {mag} | {round(dist,1)} km")
                    match = {
                        "state": office["state"], "capacity": office["capacity"],
                        "mag": mag, "dist": dist, "depth": round(eq_depth, 1),
                        "depth_type": depth_label, "place": place, "tier_label": tier_label
                    }
                    (tier1_matches if tier == 1 else tier2_matches).append(match)
                    new_ids.add(event_id)

        if tier1_matches or tier2_matches:
            send_combined_alert(tier1_matches, tier2_matches)
            seen_ids.update(new_ids)
            save_seen_ids(seen_ids)
        else:
            print("No offices within risk zone. No alert sent.")

    except requests.exceptions.ConnectionError:
        print("Network error — cannot reach API")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Timeout — API too slow")
        sys.exit(1)
    except requests.exceptions.JSONDecodeError as e:
        print(f"Bad JSON response: {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"Missing column in CSV: {e} — check offices.csv headers")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error — {type(e).__name__}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
