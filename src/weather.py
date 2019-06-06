import requests
import os
from dotenv import load_dotenv
import logging
import tzlocal
from uszipcode import SearchEngine
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv()


def get_daily_values(item):
    return datetime.fromtimestamp(float(item['time']), tzlocal.get_localzone())


class DarkSkyApi(object):
    def __init__(self, zipcode, request_type):
        """ initialize coordinates and request """
        self.zipcode = zipcode
        self.request_type = request_type

        # print(self._coords)


        self.search = SearchEngine(simple_zipcode=True)
        self.addr = self.search.by_zipcode(self.zipcode)
        # self.LATITUDE = self._coords.get("latitude")
        # self.LONGITUDE = self._coords.get("longitude")
        self.LATITUDE = self.addr.lat
        self.LONGITUDE = self.addr.lng



        # default to LR
        if self.LATITUDE is None or self.LONGITUDE is None:
            self.LATITUDE = os.getenv("LITTLE_ROCK_LAT")
            self.LONGITUDE = os.getenv("LITTLE_ROCK_LONG")

        self.weatherRequest = "https://api.darksky.net/forecast/75a9e562db1e04cbb51a8af5ee22b6b5/{},{}?exclude=flags, " \
                              "minutely".format(self.LATITUDE, self.LONGITUDE)


    def get_weather(self):
        """ get weather from api and run it through parsing functions """

        print("Getting Weather JSON From API")
        weather_json = requests.get(self.weatherRequest).json()

        parsed_json = None
        try:
            weather_json["error"]
        except KeyError:
            parsed_json = self.parse_weather_json(weather_json)

        if parsed_json and self.request_type == "current":
            speech_text = self.build_current_weather_reply(parsed_json)
        elif parsed_json and self.request_type == "hourly":
            speech_text = self.build_daily_weather_reply(parsed_json)
        elif parsed_json and self.request_type == "daily":
            speech_text = self.build_hourly_weather_reply(parsed_json)
        else:
            speech_text = "Sorry, incorrect location for retrieving weather."

        return speech_text

    def parse_weather_json(self, weather_json):
        """ parse weather json from api """

        currentWeatherSummary = weather_json['currently']['summary']
        hourlyWeatherSummary = weather_json['hourly']['summary']
        dailyWeatherSummary = weather_json['daily']['summary']
        ct = self.convert_ts(weather_json['currently']['time'], tzlocal.get_localzone())
        # ht = self.convert_ts(weather_json['hourly']['time'], tzlocal.get_localzone())
        # dt = self.convert_ts(weather_json['daily']['time'], tzlocal.get_localzone())



        hourly_list = weather_json['hourly']['data']
        hourly_times = list(map(lambda d: d['time'], hourly_list))
        i = 0
        while i < len(hourly_times):
            hourly_times[i] = self.convert_ts(hourly_times[i], tzlocal.get_localzone())
            i += 1

        daily_list = weather_json['daily']['data']
        daily_times = list(map(lambda d: d['time'], daily_list))
        i = 0
        while i < len(daily_times):
            daily_times[i] = self.convert_ts(daily_times[i], tzlocal.get_localzone())
            i += 1

        print(hourly_times)
        print(daily_times)
        print(ct)

        parsed_weather_json = {
            "current_weather": currentWeatherSummary,
            "hourly_weather": hourlyWeatherSummary,
            "daily_weather": dailyWeatherSummary,
            "current_time": ct
        }

        try:
            alerts = weather_json['alerts']
        except KeyError as e:
            print(e)
            alerts = None

        res = {}
        if alerts:
            for line in alerts:
                res.update(line)

        for key in res:
            parsed_weather_json.update({ "alert_" + key: res['{}'.format(key)] })

        print(parsed_weather_json)
        return parsed_weather_json

    def build_current_weather_reply(self, parsed_json):
        speech_text = "The current forecast is "
        speech_text += parsed_json["current_weather"] + "."
        speech_text += " The current time is " + parsed_json['current_time'] + "."
        return speech_text

    def build_hourly_weather_reply(self, parsed_json):
        speech_text = "The hourly forecast is "
        speech_text += parsed_json["hourly_weather"] + "."
        return speech_text

    def build_daily_weather_reply(self, parsed_json):
        speech_text = "The daily forecast is "
        speech_text += parsed_json["daily_weather"]
        return speech_text

    def convert_ts(self, ts, tz):
        return datetime.fromtimestamp(int(ts), tz).strftime('%Y-%m-%d %I:%M %p')

def main():
    weather_coords = {
        "latitude": os.getenv("LITTLE_ROCK_LAT"),
        "longitude": os.getenv("LITTLE_ROCK_LONG"),
    }

    weatherObj = DarkSkyApi("72023", "current")
    weather_dict = weatherObj.get_weather()
    print(weather_dict)


if __name__ == "__main__":
    main()