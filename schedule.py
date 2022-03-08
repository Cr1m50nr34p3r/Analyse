#!/usr/bin/python
############################################################
###          _              _       _                    ###
### ___  ___| |__   ___  __| |_   _| | ___   _ __  _   _ ###
###/ __|/ __| '_ \ / _ \/ _` | | | | |/ _ \ | '_ \| | | |###
###\__ \ (__| | | |  __/ (_| | |_| | |  __/_| |_) | |_| |###
###|___/\___|_| |_|\___|\__,_|\__,_|_|\___(_) .__/ \__, |###
###                                         |_|    |___/ ###
############################################################
### Imports
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import argparse
import platform
from rich import pretty, print

pretty.install()
### Variables
system = platform.system()
# If modifying these scopes, delete the file /etc/1337/Analyse/token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
# edit and fill in the calendar ids which can be found in google calendar settings under the settings for specefic label
# Use format "{label}": "{cal_id}"
cal_ids = {
    "REGULAR": "akshatgarg789@gmail.com",
}
### Parser
parser = argparse.ArgumentParser(description='Import google calendar events to doom emacs')
parser.add_argument('-n',  type=int, required=False,  default=0,  help="day for example 1 = tomorrow default is 0 i.e. today")
parser.add_argument('--md', type=bool, required=False, default=True, help="save output in markdown")
args = parser.parse_args()
day_num = args.n
md = args.md


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    events = []
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
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
            year=now_dt.year, month=now_dt.month, day=now_dt.day + day_num
        ).isoformat()
        + "Z"
    )
    time_max = (
        datetime.datetime(
            year=now_dt.year, month=now_dt.month, day=now_dt.day + day_num + 1
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


def init_db():
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
    return events_db


def md():
    if system == "Windows":
        logs_dir = os.getenv('USERPROFILE').replace('\\',  '/')
        +"/Desktop/.dlogs/.Schedule/"
    else:
        logs_dir = os.getenv('HOME')+"/.dlogs/.Schedule/"
    now_dt = datetime.datetime.now()
    date = (
        datetime.datetime(
            year=now_dt.year, month=now_dt.month, day=now_dt.day + day_num
        )
    )

    def_date = str(round(int(date.strftime("%Y")),  -1)) + "s/" + date.strftime("%Y") + "/" + date.strftime("%b")
    if not os.path.exists(logs_dir+def_date):
        os.makedirs(logs_dir+def_date)
    sch = logs_dir+def_date + "/" + date.strftime('%d-%m-%Y')
    with open(f"{sch}.md", 'w') as f:
        f.write("| Time | Name |\n")
        f.write("| :---: | :--: |")
    events_db = init_db()
    for event in events_db:
        name = event.get("name")
        category = event.get("category")
        if category is None:
            category = "REGULAR"
        with open(f"{sch}.md", 'a') as f:
            f.write(f"\n| {event.get('start')} | {name} [{category}] |")


if __name__ == "__main__":
    print("getting events.....")
    events_db = init_db()
    for event in events_db:
        name = event.get("name")
        category = event.get("category")
        if category is None:
            category = "REGULAR"
        print(event.get("start"))
        print(f"  | {name} [{category}]")
        print(event.get("end"))
        print()
    if md:
        print("saving output to md")
        md()
