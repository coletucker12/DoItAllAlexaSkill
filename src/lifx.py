import requests
import os
import json
import traceback

from dotenv import load_dotenv, find_dotenv
import logging
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response


def respond(err, res=None):
    return {
        "statusCode": "400" if err else "200",
        "body": err["message"] if err else json.dumps(res),
        "headers": {"Content-Type": "application/json"},
    }


try:
    from weather import DarkSkyApi
except Exception as e:
    error = str(e)
    stacktrace = json.dumps(traceback.format_exc())
    message = "Exception: " + error + "  Stacktrace: " + stacktrace
    err = {"message": message}
    print(respond(err))


sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dotenv_path = find_dotenv(usecwd=True)
load_dotenv(dotenv_path)
LITTLE_ROCK_LAT = 34.746483
LITTLE_ROCK_LONG = -92.289597


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """ Handler for the LIFX Lights Skill"""
    # type: HandlerInput -> Response
    speech_text = "Welcome to the LIFX Skills Kit, what would you like to do?"

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello!", speech_text)).set_should_end_session(
            False)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("GetCurrentWeather"))
def get_current_weather_handler(handler_input):
    # type: (HandlerInput) -> Response

    weather_coords = {
        "latitude": LITTLE_ROCK_LAT,
        "longitude": LITTLE_ROCK_LONG,
    }
    print(weather_coords)

    weatherObj = DarkSkyApi("75a9e562db1e04cbb51a8af5ee22b6b5", weather_coords)
    weather_dict = weatherObj.get_weather()

    if weather_dict:
        speech_text = "The current forecast is "
        speech_text += weather_dict["current_weather"]

        speech_text += ". The hourly forecast is "
        speech_text += weather_dict["hourly_weather"]

        speech_text += ". The daily forecast is "
        speech_text += weather_dict["daily_weather"]
    else:
        speech_text = "Sorry, incorrect location for retrieving weather."

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello!", speech_text)).ask("Anything else?")
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("TurnOnAllLights"))
def turn_on_all_lights_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "Turning On All Of The Lights"

    weather_request = "https://api.darksky.net/forecast/75a9e562db1e04cbb51a8af5ee22b6b5/34.746483,-92.28959"
    weather_json = requests.get(weather_request).json()
    speech_text += weather_json['timezone']

    reprompt = "Anything else fadshfhau?"
    handler_input.response_builder.speak(speech_text).set_should_end_session(False).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "You can say hello to me!"

    handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
        SimpleCard("Hello World", speech_text))
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda handler_input :
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "Goodbye!"

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello World", speech_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallBackIntent"))
def fallback_intent_handler(handler_input):
    """
    AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    # type: (HandlerInput) -> Response
    speech_text = (
        "The Hello World skill can't help you with that.  "
        "You can say hello!!")
    reprompt = "You can say hello!!"
    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    # type: (HandlerInput) -> Response
    # any cleanup logic goes here

    return handler_input.response_builder.response


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    # type: (HandlerInput, Exception) -> Response
    # Log the exception in CloudWatch Logs
    print(exception)

    speech = "Sorry, I didn't get it. Can you please say it again!!"
    handler_input.response_builder.speak(speech).ask(speech)
    return handler_input.response_builder.response


handler = sb.lambda_handler()
