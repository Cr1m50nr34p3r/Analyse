import schedule
import os
import datetime
# change these variables
# directory where the logs of track.py are ituated
logs_dir=""
# fill the list with calendar labels from your google calendar
names=[]
# permanent variables
current_date=datetime.datetime.now().date()
current_date="{:04d}-{:02d}-{:02d}".format(current_date.year,current_date.month,current_date.day)
# Functions
def check_log(date):
    logs=os.listdir(logs_dir)
    for log in logs:
        log_list=log.split('.')
        log=log_list[0]
        if log==date:
            log_read= open(f"{logs_dir}/{log}.bin",'rb')
            data=log_read.read()
            return (data.decode('ascii'))
def read_log(date,name):
    start_times=[]
    end_times=[]
    durations=[]
    tds=datetime.timedelta()
    data=check_log(date)
    data=data.splitlines()
    for line in data:
        line_l=line.split(' - ')
        if line_l[0]==name.upper():
            start_times.append(line_l[1])
            end_times.append(line_l[2])
            durations.append(line_l[3])
    for duration in durations:
        dur=datetime.datetime.strptime(duration,"%H:%M:%S")
        td=datetime.timedelta(hours=dur.hour,minutes=dur.minute,seconds=dur.second)
        tds+=td
    whitespaces=len(name)+3
    return tds
def duration(events):
    durations=[]
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
   
# execute
if __name__=="__main__":
    print('Getting the events ....')
    for name in names:
        try:
            durations_cal=duration(schedule.get_events())
            td_cal=datetime.timedelta()
            for td in durations_cal:
                td_cal+=td
            tds=read_log(current_date,name.upper())
            if td_cal>tds:
                print(f"you performed task {name.upper()} for {td_cal-tds} less time")
            elif tds>td_cal:
                print(f"you performed task {name.upper()} for {tds-td_cal} more")
        except TypeError:
            print(f"you did not schedule task {name.upper()} or did not do it") 
