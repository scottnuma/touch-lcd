"""A proof of concept of Python's ability to use show useful daily info"""

import quick_start as cal
import pytz, os, pyowm
from datetime import datetime
import easy_cereal
import time

# Import the calendar ID's from environment variables to protect privacy
calendarIds = { 'classes':os.environ['CLASSES_CALENDAR_ID'],'main':os.environ['MAIN_CALENDAR_ID']}

def get_weather():
    """Returns a dictionary of weather information

    Dictionary contains the high and low as well as
    the current temperature and sky appearance
    """
    owm = pyowm.OWM(os.environ['OPEN_WEATHER_API_KEY'])
    city = 'Irvine,us'
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
    start_string = event['start']['dateTime'][11:-9]
    end_string = event['end']['dateTime'][11:-9]
    return "" + twelve_hour(start_string) + " - " + twelve_hour(end_string) + " " + event['summary']

def twelve_hour(time):
    """Converts a time string from military to standard time"""
    hour_min = time.split(":")
    hour_num = int(hour_min[0])
    if hour_num > 12:
        return str((hour_num) - 12) + ":" + hour_min[1]
    else:
        return time

def weather_string(weather):
    """Formats the weather into a string tuple"""
    a = "Today will have a low of %s and a high of %s." % (weather['low'], weather['high'])
    b = "Currently it is %s with a %s." % (weather['current'], weather['status'])
    return (a,b)


def main():
    calA = get_events('main')
    calB = get_events('classes')
    combined_classes = calB + calA
    combined_classes.sort(key=lambda e:e['start']['dateTime'])


    lcd = easy_cereal.Display()
    lcd.cmd('colorid 17 3 3 3')
    lcd.cmd('cls 17')
    lcd.cmd("cls black white")
    lcd.new_line()
    lcd.print("Calendar")
    lcd.new_line()
    lcd.new_line()

    if not combined_classes:
        lcd.print('No upcoming events found.')

    for event in combined_classes:
        lcd.print(format_event(event))
        lcd.new_line()

    lcd.new_line()
    lcd.print("Weather")
    weather_str = weather_string(get_weather())
    lcd.new_line()
    lcd.new_line()
    lcd.print(weather_str[0])
    lcd.new_line()
    lcd.print(weather_str[1])

    # Refresh the screen after 5 minutes
    time.sleep(5 * 60)


if __name__ == "__main__":
    while(True):
        main()
