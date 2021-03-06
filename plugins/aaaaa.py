from util import hook
import requests

@hook.command
def openweather(inp):
    try:
        data = requests.get('http://api.openweathermap.org/data/2.5/find?q={0}&type=like'.format(inp)).json()
        city = data["list"][0]["name"]
        longitude = data["list"][0]["coord"]["lon"]
        latitude = data["list"][0]["coord"]["lat"]
        temp_K = int(data["list"][0]["main"]["temp"])
        temp_C = temp_K - 273
        temp_F = int((temp_K - 273.15) * 1.8 + 32)
        pressure = data["list"][0]["main"]["pressure"]
        humidity = data["list"][0]["main"]["humidity"]
        wind_speed = data["list"][0]["wind"]["speed"]
        wind_degree = data["list"][0]["wind"]["deg"]
        clouds_percent = data["list"][0]["clouds"]["all"]
        clouds_description = data["list"][0]["weather"][0]["description"]
        condition = {city, longitude, latitude, temp_K, temp_C, temp_F, pressure, humidity, wind_speed, wind_degree, clouds_percent, clouds_description}
        return condition
    except:
        return "Location not found"
