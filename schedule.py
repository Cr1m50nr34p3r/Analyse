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
import shutil

pretty.install()
# Variables
system = platform.system()
# If modifying these scopes, delete the file /etc/1337/Analyse/token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar/"]
# TIMEZONE = 'India/Kolkata'
TIMEZONE = 'UTC'
dGMT = datetime.timedelta(hours=-5, minutes=-30)
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
parser.add_argument('--md', action='store_true', required=False, help="save/upload output in markdown file")
parser.add_argument('-u', action='store_true', required=False, help="wheather to upload the file or write to it")
args = parser.parse_args()
day_num = args.n
is_md = args.md
is_upload = args.u


def print_center_text(text: str):
    if system == "Windows":
        os.system('cls')
    else:
        os.system('clear')
    center_line = int(shutil.get_terminal_size().lines/2-text.count('\n')+1)
    print('\n'*center_line)
    ltext = text.splitlines()
    for line in ltext:
        s = line.center(shutil.get_terminal_size().columns)
        print(s)
    print('\n'*center_line)
    if system == "Windows":
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break


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


def init_api():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        try:
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        except google.auth.exceptions.RefreshError:
            print_center_text("token.pickle expired creating new one ....")
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
    return service


def get_events():
    events = []
    # Set up Time variables
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
    service = init_api()
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
    events_db = get_events()
    for event in events_db:
        name = event.get("name")
        if name is None:
            name = "UNTITLED"
        category = event.get("category")
        if category is None:
            category = "REGULAR"
        with open(f"{file}.md", 'a') as f:
            f.write(f"\n| {event.get('start')} | {name} [{category}] |")


def parse_md():
    event_db = []
    now_dt = datetime.datetime.now()
    file = get_file() + ".md"
    if not os.path.isfile(file) or os.stat(file).st_size == 0:
        print_center_text(f"file {file} either does not exist or is empty")
        sys.exit()
    with open(file, 'r') as buffer:
        lines = buffer.readlines()
        if len(lines) < 3:
            print_center_text(f"file {file} only contains less than 3 lines as read function would not work the system is exiting")
            sys.exit()
        elif len(lines) == 3:
            line = lines[2]
            columns = line.split(' | ')
            start_time = (datetime.datetime.strptime(columns[0].replace('| ', ''), "%H:%M:%S").replace(year=now_dt.year, day=now_dt.day + day_num, month=now_dt.month) + dGMT).isoformat()
            name = columns[1].split('[')[0]
            label = columns[1].split('[')[1].replace('] |\n', '')
            end_time = (datetime.datetime(
                year=now_dt.year, month=now_dt.month, day=now_dt.day + day_num + 1
            ) + dGMT).isoformat()
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
                start_time = (datetime.datetime.strptime(columns[0].replace('| ', ''), "%H:%M:%S").replace(year=now_dt.year, day=now_dt.day + day_num, month=now_dt.month) + dGMT).isoformat()
                name = columns[1].split('[')[0]
                label = columns[1].split('[')[1].replace('] |\n', '')
                end_time = (datetime.datetime.strptime(lines[lc+1].split(' | ')[0].replace('| ', ''), "%H:%M:%S").replace(year=now_dt.year, day=now_dt.day + day_num, month=now_dt.month) + dGMT).isoformat()
                event = {
                        'name': name,
                        'label': label,
                        'start_time': start_time,
                        'end_time': end_time
                        }
                event_db.append(event)
            line = lines[-1]
            columns = line.split(' | ')
            start_time = (datetime.datetime.strptime(columns[0].replace('| ', ''), "%H:%M:%S").replace(year=now_dt.year, day=now_dt.day + day_num, month=now_dt.month) + dGMT).isoformat()
            name = columns[1].split('[')[0]
            label = columns[1].split('[')[1].replace('] |\n', '')
            end_time = (datetime.datetime(
                year=now_dt.year, month=now_dt.month, day=now_dt.day + day_num + 1
            ) + dGMT).isoformat()
            event = {
                    'name': name,
                    'label': label,
                    'start_time': start_time,
                    'end_time': end_time
                    }
            event_db.append(event)
        return event_db


def upload_md():
    print("Reading file ...")
    event_db = parse_md()
    for data in event_db:
        event = {
                'summary': data['name'],
                'start': {
                    'dateTime': f"{data['start_time']}Z",
                    'TimeZone': TIMEZONE
                    },
                'end': {
                    'dateTime': f"{data['end_time']}Z",
                    'TimeZone': TIMEZONE
                    }
                }
        print("Uploading events")
        service = init_api()
        if data['label'] == "REGULAR":
            cal_ids['REGULAR'] = 'primary'
        event = service.events().insert(calendarId=cal_ids[data['label']], body=event).execute()
        print(f"Event created at {event.get('htmlLink')}")


if __name__ == "__main__":
    if not is_upload:
        print_center_text("getting events.....")
        output = ""
        events_db = get_events()
        for event in events_db:
            name = event.get("name")
            if name is None:
                name = "UNTITLED"
            category = event.get("category")
            if category is None:
                category = "REGULAR"
            output += event.get("start") 
            output += f"  | {name} [{category}]" + " | "
            output += event.get("end") + "\n"
        print_center_text(output)
        if is_md:
            print(f"SAVING OUTPUT TO MD FILE {get_file()}")
            write_md()
    else:
        upload_md()
