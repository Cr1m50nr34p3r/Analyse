from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
cal_ids={
    "REGULAR" : "akshatgarg789@gmail.com",
    "CODING" : "e8mol2i2k4kbv84j8avaml3nkc@group.calendar.google.com",
    "TUITION": "osak0b7r51329ob7re35qfnves@group.calendar.google.com",
    "STUDY": 'tqnor6go6aafauutj6r5c7jqn4@group.calendar.google.com',
    "GAME" : "to7hn4rd6amosc2jd317n26kbg@group.calendar.google.com",
    "SCHOOL": "2k7j09evrdkmmoqf231nurgjho@group.calendar.google.com",
    "VMC":"t62kl99bos1gpgq2vs03bu3m80@group.calendar.google.com"
    }

def main(cal_id):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    durations=[]
    cal=cal_ids.get(cal_id.upper())
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    now_dt=datetime.datetime.now()
    time_min= datetime.datetime(year=now_dt.year,month=now_dt.month,day=now_dt.day,hour=0,minute=0,second=0).isoformat() + 'Z'
    events_result = service.events().list(calendarId=cal, timeMin=time_min,
                                        maxResults=20, singleEvents=True,
                                        orderBy='startTime',timeMax=now,).execute()
    events = events_result.get('items', [])
    if not events:
        return None
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        start=start.split("T")[1]
        end=end.split("T")[1]
        start=start.split("+")[0]
        end=end.split("+")[0]
        start_time=datetime.datetime.strptime(start,"%H:%M:%S")
        end_time=datetime.datetime.strptime(end,"%H:%M:%S")
        duration=end_time-start_time
        durations.append(duration)
    return durations

if __name__ == '__main__':
    durations=main(sys.argv[1])
    print(durations)