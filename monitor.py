import requests

# 1. YOUR WORKFLOW URL
URL = "https://defaultfe1d95a94ce141a58eab6dd43aa26d.9f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/c2bbf7a14d584876a3b81a8a7fbedbac/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=20YX9Mf323evgcxN68y6fdUcQWBdLxbtuEUJsnP1bcU"

def test_connection():
    # This is the simplest "Adaptive Card" format for Power Automate
    payload = {
        "type": "message",
        "attachments":,
                "$schema": "http://adaptivecards.io"
            }
        }]
    }

    print("Sending test message...")
    try:
        response = requests.post(URL, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()
