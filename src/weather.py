import requests
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv()


class DarkSkyApi(object):
    def __init__(self, secret_key, coordinate_dict):
        """ initialize coordinates and request """
        self._secret_key = secret_key
        self._coords = coordinate_dict

        print(self._coords)

        self.LATITUDE = self._coords.get("latitude")
        self.LONGITUDE = self._coords.get("longitude")

        # default to LR
        if self.LATITUDE is None or self.LONGITUDE is None:
            self.LATITUDE = os.getenv("LITTLE_ROCK_LAT")
            self.LONGITUDE = os.getenv("LITTLE_ROCK_LONG")

        self.weatherRequest = "https://api.darksky.net/forecast/{}/{},{}?exclude=flags, " \
                              "minutely".format(self._secret_key, self.LATITUDE, self.LONGITUDE)

        print(self.weatherRequest)

    def get_weather(self):
        """ get weather from api and run it through parsing functions """

        print("Getting Weather JSON From API")
        weather_json = requests.get(self.weatherRequest).json()
        parsed_json = None

        try:
            weather_json["error"]
        except KeyError:
            parsed_json = self.parse_weather_json(weather_json)

        return parsed_json

    def parse_weather_json(self, weather_json):
        """ parse weather json from api """

        print(weather_json)
        currentWeatherSummary = weather_json['currently']['summary']
        hourlyWeatherSummary = weather_json['hourly']['summary']
        dailyWeatherSummary = weather_json['daily']['summary']

        # OPTIONAL ALERTS
        # try:
        #     alerts = self.weatherJson['alerts']
        # except KeyError as e:
        #     alerts = None


        parsed_weather_json = {
            "current_weather": currentWeatherSummary,
            "hourly_weather": hourlyWeatherSummary,
            "daily_weather": dailyWeatherSummary
        }

        print(parsed_weather_json)

        return parsed_weather_json


def main():
    weather_coords = {
        "latitude": os.getenv("LITTLE_ROCK_LAT"),
        "longitude": os.getenv("LITTLE_ROCK_LONG"),
    }

    weatherObj = DarkSkyApi("75a9e562db1e04cbb51a8af5ee22b6b5", weather_coords)
    weather_dict = weatherObj.get_weather()


if __name__ == "__main__":
    main()