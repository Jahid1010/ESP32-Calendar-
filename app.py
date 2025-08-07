from flask import Flask, jsonify
import requests
import datetime
import os

app = Flask(__name__)

# --- OAuth2 Credentials ---
CLIENT_ID = "6489984974-22850tkegehk476pviiv3i5sc8fqu759.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REFRESH_TOKEN = "1//04zEPCFweUXjPCgYIARAAGAQSNwF-L9IrTZDqG7TmmOro-Q-LGUo0rhe68VY9X0pRwkLvr9fcDyGe0HcHrTYImVndadywmzp4s3k"

# Your calendar ID. "primary" = main calendar
CALENDAR_ID = "primary"

def get_access_token():
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }

    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

def get_upcoming_events(access_token, max_results=5):
    now = datetime.datetime.utcnow().isoformat() + "Z"  # UTC time
    url = f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "timeMin": now,
        "maxResults": max_results,
        "singleEvents": True,
        "orderBy": "startTime"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    events = response.json().get("items", [])
    simplified_events = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        simplified_events.append({
            "summary": event.get("summary", "No Title"),
            "start": start
        })

    return simplified_events

@app.route("/")
def index():
    return "Google Calendar API is working."

@app.route("/events")
def events():
    try:
        access_token = get_access_token()
        events = get_upcoming_events(access_token)
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
