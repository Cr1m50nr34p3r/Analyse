#!/usr/bin/python
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys

# If modifying these scopes, delete the file /etc/1337/Analyse/token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
# edit and fill in the calendar ids which can be found in google calendar settings under the settings for specefic label
cal_ids = {
    "REGULAR": "akshatgarg789@gmail.com",
    "STUDY": "tqnor6go6aafauutj6r5c7jqn4@group.calendar.google.com",
    "REST": "to7hn4rd6amosc2jd317n26kbg@group.calendar.google.com",
    "HW": "2k7j09evrdkmmoqf231nurgjho@group.calendar.google.com",
    "EXTRA": "t62kl99bos1gpgq2vs03bu3m80@group.calendar.google.com",
    "CLASSES": "hs2frss259nb72ho1bjtut8j6o@group.calendar.google.com",
}


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    events = []
    durations = []
    event_name = []
    event_names_temp = []
    creds = None
    # The file /etc/1337/Analyse/token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    now_dt = datetime.datetime.now()
    time_min = (
        datetime.datetime(
            year=now_dt.year, month=now_dt.month, day=now_dt.day
        ).isoformat()
        + "Z"
    )
    time_max = (
        datetime.datetime(
            year=now_dt.year, month=now_dt.month, day=now_dt.day + 1
        ).isoformat()
        + "Z"
    )
    for cal_id in cal_ids:

        cal = cal_ids.get(cal_id.upper())
        events_result = (
            service.events()
            .list(
                calendarId=cal,
                timeMin=time_min,
                maxResults=20,
                singleEvents=True,
                orderBy="startTime",
                timeMax=time_max,
            )
            .execute()
        )
        events += events_result.get("items", [])
    return events


if __name__ == "__main__":
    events = main()
    events_db = []
    for event in events:
        start = (
            event["start"]
            .get("dateTime", event["start"].get("date"))
            .split("T")[1]
            .split("+")[0]
        )
        end = (
            event["end"]
            .get("dateTime", event["end"].get("date"))
            .split("T")[1]
            .split("+")[0]
        )
        category = event.get("organizer").get("displayName")
        name = event.get("summary")
        events_db.append(
            {"start": start, "end": end, "name": name, "category": category}
        )
    events_db = sorted(events_db, key=lambda i: i["start"])
    for event in events_db:
        name = event.get("name")
        category = event.get("category")
        if category == None:
            category = "REGULAR"
        print(event.get("start"))
        print(f"  | {name} [{category}]")
        print(event.get("end"))
        print()
