import requests
import os
import json
import traceback

from dotenv import load_dotenv, find_dotenv
import logging
from ask_sdk_core.skill_builder import SkillBuilder, CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.ui import SimpleCard, AskForPermissionsConsentCard
from ask_sdk_model import Response
from ask_sdk_model.services import ServiceException


permissions = ["read::alexa:device:all:address:country_and_postal_code"]
WELCOME = ("Welcome to the Do It All Smart Home Skill "
           "You can ask this app to do many things. "
           "What do you want to ask?")
WHAT_DO_YOU_WANT = "What do you want to ask?"
NOTIFY_MISSING_PERMISSIONS = ("Please enable Location permissions in "
                              "the Amazon Alexa app.")
NO_ADDRESS = ("It looks like you don't have an address set. "
              "You can set your address from the companion app.")
ADDRESS_AVAILABLE = "Here is your full address: {}, {}, {}"
ERROR = "Uh Oh. Looks like something went wrong."
LOCATION_FAILURE = ("There was an error with the Device Address API. "
                    "Please try again.")
GOODBYE = "Bye! Thanks for using the Do It All Smart Home Skill!"
UNHANDLED = "This skill doesn't support that. Please ask something else"
HELP = ("You can use this skill by asking something like: "
        "Whats the current weather? or Turn on all my lights")


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


sb = CustomSkillBuilder(api_client=DefaultApiClient())
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

    handler_input.response_builder.speak(WELCOME).set_card(
        SimpleCard(WHAT_DO_YOU_WANT)).set_should_end_session(
            False)
    return handler_input.response_builder.response


"""
    ---------------------------------
    Handlers for Weather
    ---------------------------------
"""


@sb.request_handler(can_handle_func=is_intent_name("GetCurrentWeather"))
def get_current_weather_handler(handler_input):
    # type: (HandlerInput) -> Response

    req_envelope = handler_input.request_envelope
    service_client_fact = handler_input.service_client_factory

    if not (req_envelope.context.system.user.permissions and
            req_envelope.context.system.user.permissions.consent_token):
        handler_input.response_builder.speak("You are missing permissions")
        handler_input.response_builder.set_card(
            AskForPermissionsConsentCard(permissions=permissions))
        return handler_input.response_builder.response

    try:
        device_id = req_envelope.context.system.device.device_id
        device_addr_client = service_client_fact.get_device_address_service()
        addr = device_addr_client.get_country_and_postal_code(device_id)

        if addr.postal_code is None and addr.country_code is None:
            handler_input.response_builder.speak("You have no address")
        else:
            weatherObj = DarkSkyApi(addr.postal_code, "current")
            speech_text = weatherObj.get_weather()
            handler_input.response_builder.speak(speech_text)
        return handler_input.response_builder.response
    except ServiceException:
        handler_input.response_builder.speak("Looks like something went wrong")
        return handler_input.response_builder.response
    except Exception as e:
        raise e


    # handler_input.response_builder.speak(speech_text).set_card(
    #     SimpleCard("Hello!", speech_text)).ask("Anything else?")
    # return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("GetHourlyWeather"))
def get_hourly_weather_handler(handler_input):
    # type: (HandlerInput) -> Response

    weather_coords = {
        "latitude": LITTLE_ROCK_LAT,
        "longitude": LITTLE_ROCK_LONG,
    }

    weatherObj = DarkSkyApi(weather_coords, "hourly")
    speech_text = weatherObj.get_weather()

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello!", speech_text)).ask("Anything else?")
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("GetDailyWeather"))
def get_daily_weather_handler(handler_input):
    # type: (HandlerInput) -> Response

    weather_coords = {
        "latitude": LITTLE_ROCK_LAT,
        "longitude": LITTLE_ROCK_LONG,
    }

    weatherObj = DarkSkyApi(weather_coords, "daily")
    speech_text = weatherObj.get_weather()

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

    handler_input.response_builder.speak(HELP).ask(HELP)
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda handler_input :
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "Goodbye!"

    handler_input.response_builder.speak(GOODBYE)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallBackIntent"))
def fallback_intent_handler(handler_input):
    """
    AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    # type: (HandlerInput) -> Response

    handler_input.response_builder.speak(UNHANDLED).ask(HELP)
    return handler_input.response_builder.response


@sb.exception_handler(can_handle_func=ServiceException)
def get_address_exception_handler(handler_input, exception):
    if exception.status_code == 403:
        handler_input.response_builder.speak(
            NOTIFY_MISSING_PERMISSIONS).set_card(
            AskForPermissionsConsentCard(permissions=permissions))
    else:
        handler_input.response_builder.speak(
            LOCATION_FAILURE).ask(LOCATION_FAILURE)

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
    print("Encountered the following exception: {}".format(exception))

    speech = "Sorry, I didn't get it. Can you please say it again!!"
    handler_input.response_builder.speak(speech).ask(speech)
    return handler_input.response_builder.response


handler = sb.lambda_handler()
