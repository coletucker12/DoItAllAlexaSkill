import argparse
import requests
import logging

# from ask_sdk_core.skill_builder import SkillBuilder
# from ask_sdk_core.dispatch_components import AbstractRequestHandler
# from ask_sdk_core.dispatch_components import AbstractExceptionHandler
# from ask_sdk_core.utils import is_request_type, is_intent_name
# from ask_sdk_core.handler_input import HandlerInput
#
# from ask_sdk_model.ui import SimpleCard
# from ask_sdk_model import Response
#
# sb = SkillBuilder()
#
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


def main():
    print("testing weather api")
    # logger.info("Reading in secure token...")
    # parser = argparse.ArgumentParser()
    # parser.add_argument('token', help="Secure token for API auth")
    # user_token = parser.parse_args();

    LATITUDE = "34.746483"
    LONGITUDE = "-92.289597"
    weatherRequest = "https://api.darksky.net/forecast/75a9e562db1e04cbb51a8af5ee22b6b5/{},{}?exclude=flags, minutely".format(
        LATITUDE, LONGITUDE)
    weatherJson = requests.get(weatherRequest).json()
    currentWeatherSummary = weatherJson['timezone']
    print(type(currentWeatherSummary))
    print(currentWeatherSummary)



if __name__ == "__main__":
    main()