from flask import Flask, jsonify
import requests
import datetime
import os
from urllib.parse import quote

app = Flask(__name__)

# --- Your OAuth2 Credentials ---
CLIENT_ID = "6489984974-22850tkegehk476pviiv3i5sc8fqu759.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REFRESH_TOKEN = "1//04zEPCFweUXjPCgYIARAAGAQSNwF-L9IrTZDqG7TmmOro-Q-LGUo0rhe68VY9X0pRwkLvr9fcDyGe0HcHrTYImVndadywmzp4s3k"

# Calendars to fetch from
CALENDAR_IDS = [
    "primary",
    "addressbook#contacts@group.v.calendar.google.com",  # Birthdays
    "en.bd#holiday@group.v.calendar.google.com"          # Bangladesh Public Holidays
]

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

def get_upcoming_events(access_token, calendar_id, max_results=20):
    now = datetime.datetime.utcnow().isoformat() + "Z"  # UTC time
    encoded_calendar_id = quote(calendar_id, safe='')
    url = f"https://www.googleapis.com/calendar/v3/calendars/{encoded_calendar_id}/events"
    headers = {"Authorization": f"Bearer {access_token}"}
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
        all_events = []
        for cal_id in CALENDAR_IDS:
            events = get_upcoming_events(access_token, cal_id)
            all_events.extend(events)
        all_events.sort(key=lambda e: e["start"])
        return jsonify(all_events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
