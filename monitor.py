def send_teams_alert(office, mag, dist, place):
    # Modern Workflows format
    payload = {
        "text": (
            f"⚠️ EARTHQUAKE ALERT\n\n"
            f"Site: {office['site']} ({office['state']})\n"
            f"Magnitude: {mag}\n"
            f"Distance: {dist:.1f} km\n"
            f"Epicenter: {place}"
        )
    }
    # This URL will now correctly trigger the Power Automate workflow
    requests.post(https://defaultfe1d95a94ce141a58eab6dd43aa26d.9f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/c2bbf7a14d584876a3b81a8a7fbedbac/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=20YX9Mf323evgcxN68y6fdUcQWBdLxbtuEUJsnP1bcU, json=payload)
