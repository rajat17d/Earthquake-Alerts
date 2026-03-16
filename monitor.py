import requests

# Your exact Power Automate URL
URL = "https://defaultfe1d95a94ce141a58eab6dd43aa26d.9f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/c2bbf7a14d584876a3b81a8a7fbedbac/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=20YX9Mf323evgcxN68y6fdUcQWBdLxbtuEUJsnP1bcU"

def test():
    # This is a very basic message format
    payload = {"text": "Connection Test: GitHub is talking to Teams!"}
    
    try:
        print("Attempting to send message...")
        r = requests.post(URL, json=payload, timeout=10)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test()
