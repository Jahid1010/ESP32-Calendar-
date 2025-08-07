from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Replace with your own tokens
REFRESH_TOKEN = "YOUR_REFRESH_TOKEN"
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
CALENDAR_ID = "primary"  # or full calendar email

def get_access_token():
    url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    response = requests.post(url, data=payload)
    return response.json().get("access_token")

def get_calendar_events():
    token = get_access_token()
    if not token:
        return {"error": "Token fetch failed"}

    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "maxResults": 3,
        "orderBy": "startTime",
        "singleEvents": True,
        "timeMin": "2025-08-08T00:00:00Z"
    }

    url = f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events"
    response = requests.get(url, headers=headers, params=params)
    return response.json()

@app.route('/')
def index():
    return jsonify(get_calendar_events())

