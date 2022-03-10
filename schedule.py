#!/usr/bin/python
##########################################################
#           _              _       _                     #
#  ___  ___| |__   ___  __| |_   _| | ___   _ __  _   _  #
# / __|/ __| '_ \ / _ \/ _` | | | | |/ _ \ | '_ \| | | | #
# \__ \ (__| | | |  __/ (_| | |_| | |  __/_| |_) | |_| | #
# |___/\___|_| |_|\___|\__,_|\__,_|_|\___(_) .__/ \__, | #
#                                          |_|    |___/  #
##########################################################
# Imports
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import google.auth.exceptions
import argparse
import platform
import sys
from rich import pretty, print

pretty.install()
# Variables
system = platform.system()
# If modifying these scopes, delete the file /etc/1337/Analyse/token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
# edit and fill in the calendar ids which can be found in google calendar settings under the settings for specefic label
# Use format "{label}": "{cal_id}"
cal_ids = {
    "REGULAR": "akshatgarg789@gmail.com",
    "STUDY": "tqnor6go6aafauutj6r5c7jqn4@group.calendar.google.com",
    "REST": "to7hn4rd6amosc2jd317n26kbg@group.calendar.google.com",
    "HW": "2k7j09evrdkmmoqf231nurgjho@group.calendar.google.com",
    "EXTRA": "t62kl99bos1gpgq2vs03bu3m80@group.calendar.google.com",
    "CLASSES": "hs2frss259nb72ho1bjtut8j6o@group.calendar.google.com",
}
# Parser
parser = argparse.ArgumentParser(description='Import google calendar events to doom emacs')
parser.add_argument('-n',  type=int, required=False,  default=0,  help="day for example 1 = tomorrow default is 0 i.e. today")
parser.add_argument('--md', type=bool, required=False, default=True, help="save output in markdown")
args = parser.parse_args()
day_num = args.n
is_md = args.md


def get_file():
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
    return sch


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
        try:
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        except google.auth.exceptions.RefreshError:
            print("token.pickle expired creating new one ....")
            pass
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


def write_md():
    file = get_file()
    with open(f"{file}.md", 'w') as f:
        f.write("| Time | Name |\n")
        f.write("| :---: | :--: |")
    events_db = init_db()
    for event in events_db:
        name = event.get("name")
        if name is None:
            name = "UNTITLED"
        category = event.get("category")
        if category is None:
            category = "REGULAR"
        with open(f"{file}.md", 'a') as f:
            f.write(f"\n| {event.get('start')} | {name} [{category}] |")


def upload():
    event_db = []
    now_dt = datetime.datetime.now()
    file = get_file() + ".md"
    if not os.path.isfile(file) or os.stat(file).st_size == 0:
        print(f"file {file} either does not exist or is empty")
        sys.exit()
    with open(file, 'r') as buffer:
        lines = buffer.readlines()
        if len(lines) < 3:
            print(f"file {file} only contains less than 3 lines as read function would not work the system is exiting")
            sys.exit()
        elif len(lines) == 3:
            line = lines[2]
            columns = line.split(' | ')
            start_time = datetime.datetime.strptime(columns[0].replace('| ', ''), "%H:%M:%S").replace(year=now_dt.year, day=now_dt.day, month=now_dt.month)
            name = columns[1].split('[')[0]
            label = columns[1].split('[')[1].replace('] |', '')
            end_time = datetime.datetime(
                year=now_dt.year, month=now_dt.month, day=now_dt.day + day_num + 1
            ).isoformat()
            event = {
                    'name': name,
                    'label': label,
                    'start_time': start_time,
                    'end_time': end_time
                    }
            event_db.append(event)
        else:
            lines.pop(0)
            lines.pop(0)
            for lc in range(0, len(lines)-1):
                line = lines[lc]
                columns = line.split(' | ')
                start_time = datetime.datetime.strptime(columns[0].replace('| ', ''), "%H:%M:%S").replace(year=now_dt.year, day=now_dt.day, month=now_dt.month)
                name = columns[1].split('[')[0]
                label = columns[1].split('[')[1].replace('] |\n', '')
                end_time = datetime.datetime.strptime(lines[lc+1].split(' | ')[0].replace('| ', ''), "%H:%M:%S").replace(year=now_dt.year, day=now_dt.day, month=now_dt.month)
                event = {
                        'name': name,
                        'label': label,
                        'start_time': start_time,
                        'end_time': end_time
                        }
                event_db.append(event)
            line = lines[-1]
            columns = line.split(' | ')
            start_time = datetime.datetime.strptime(columns[0].replace('| ', ''), "%H:%M:%S").replace(year=now_dt.year, day=now_dt.day, month=now_dt.month)
            name = columns[1].split('[')[0]
            label = columns[1].split('[')[1].replace('] |\n', '')
            end_time = datetime.datetime(
                year=now_dt.year, month=now_dt.month, day=now_dt.day + day_num + 1
            ).isoformat()
            event = {
                    'name': name,
                    'label': label,
                    'start_time': start_time,
                    'end_time': end_time
                    }
            event_db.append(event)
    return event_db


if __name__ == "__main__":
    print(upload())
    # print("getting events.....")
    # events_db = init_db()
    # for event in events_db:
        # name = event.get("name")
        # if name is None:
            # name="UNTITLED"
        # category = event.get("category")
        # if category is None:
            # category = "REGULAR"
        # print(event.get("start"))
        # print(f"  | {name} [{category}]")
        # print(event.get("end"))
        # print()
    # if is_md:
        # print("saving output to md")
        # write_md()
