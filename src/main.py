import argparse
import logging
from .lifx import Lifx

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    print("Reading in secure token...")
    parser = argparse.ArgumentParser()
    parser.add_argument('token', help="Secure token for API auth")
    user_token = parser.parse_args();
    Lifx(token=user_token);


if __name__ == "__main__":
    main()