"""A proof of concept of Python's ability to use show useful daily info"""

import quick_start as cal
import pytz, os, pyowm
from datetime import datetime
import easy_cereal

# Import the calendar ID's from environment variables to protect privacy
calendarIds = { 'classes':os.environ['CLASSES_CALENDAR_ID'],'main':os.environ['MAIN_CALENDAR_ID']}

def get_weather():
    """Returns a dictionary of weather information

    Dictionary contains the high and low as well as
    the current temperature and sky appearance
    """
    owm = pyowm.OWM(os.environ['OPEN_WEATHER_API_KEY'])
    city = 'Berkeley,us'
    observation = owm.weather_at_place(city)
    w = observation.get_weather()
    temps = w.get_temperature('fahrenheit')
    high = round(temps['temp_max'])
    low = round(temps['temp_min'])
    current = round(temps['temp'])
    status = w.get_detailed_status()
    return {'high':high, 'low':low, 'current':current, 'status':status}

def get_events(calendar_id):
    """Returns a list of the events that happen today"""

    credentials = cal.get_credentials()
    http = credentials.authorize(cal.httplib2.Http())
    service = cal.discovery.build('calendar', 'v3', http=http)

    # Start is at 12AM
    start = datetime.now(pytz.timezone("America/Los_Angeles")).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
    start_string = str(start.isoformat())[:-6] + 'Z'

    # End is before 12AM on the next day
    end = datetime.now(pytz.timezone("America/Los_Angeles")).replace(hour=23, minute=59, second=59, microsecond=0).astimezone(pytz.utc)
    end_string = str(end.isoformat())[:-6] + 'Z'

    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    eventsResult = service.events().list(
        calendarId=calendarIds[calendar_id], timeMin=start_string, timeMax=end_string, maxResults=19, singleEvents=True,
        orderBy='startTime').execute()
    return eventsResult.get('items', [])

def cal_print(calendar):
    for event in calendar:
        print(format_event(event))

def format_event(event):
    """Returns an string with the start, end, and summary"""
    return "" + event['start']['dateTime'][11:-9] + " - " + event['end']['dateTime'][11:-9] + " " + event['summary']

calA = get_events('main')
calB = get_events('classes')
combined_classes = calB + calA
combined_classes.sort(key=lambda e:e['start']['dateTime'])

print(get_weather())

lcd = easy_cereal.Display()
lcd.cmd("cls black white")
lcd.print("Calendar")
lcd.new_line()
lcd.new_line()

if not events:
    print('No upcoming events found.')
    lcd.print('No upcoming events found.')

for event in combined_classes:
    start = event['start'].get('dateTime', event['start'].get('date'))[:10]
    print('type: %s' % type(start))
    print(start, event['summary'])
    lcd.print(start, size=20)
    lcd.print(' ', size = 20)
    lcd.print(event['summary'], size=20)
    lcd.new_line()
