import pyowm

owm = pyowm.OWM('4f4eefb23188ad8b205092b360f0e82e')  # You MUST provide a valid API key

# Search for current weather in Berkeley (US)
observation = owm.weather_at_place('Berkeley,us')
w = observation.get_weather()
print(w)                      # <Weather - reference time=2013-12-18 09:20, 
                              # status=Clouds>

# Weather details
w.get_humidity()              # 87
print(w.get_temperature('fahrenheit'))  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}

