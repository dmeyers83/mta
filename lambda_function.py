# -*- coding: utf-8 -*-

# This is a Color Picker Alexa Skill.
# The skill serves as a simple sample on how to use
# session attributes.

import logging

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard, AskForPermissionsConsentCard
from ask_sdk_model.services import ServiceException
# python standard library
import json
# third party
import requests
import xmltodict

sb = CustomSkillBuilder(api_client=DefaultApiClient()) # remove api client

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)
permissions = ["read::alexa:device:all:address"]

Subway_LIST = ["1", "2", "3", "4", "5", "6", "7", "a", "c", "e", "f", "b", "n", "r", "q", "m", "s", "j", "z", "d", "g","l"]

Subway_Status = {"1":"", "2":"", "3":"", "4":"", "5":"", "6":"", "7":"", "a":"", "c":"", "e":"", "f":"", "b":"", "n":"", "r":"",
                    "q":"", "w":"", "m":"", "s":"", "j":"", "z":"", "d":"", "g":"","l":"", "si":""}

WELCOME = ("Welcome to the Sample Device Address API Skill!  "
           "You can ask for the device address by saying what is my "
           "address.  What do you want to ask?")
WHAT_DO_YOU_WANT = "What do you want to ask?"
NOTIFY_MISSING_PERMISSIONS = ("Please enable Location permissions in "
                              "the Amazon Alexa app.")
NO_ADDRESS = ("It looks like you don't have an address set. "
              "You can set your address from the companion app.")
ADDRESS_AVAILABLE = "Here is your full address: {}, {}, {}"
ERROR = "Uh Oh. Looks like something went wrong."
LOCATION_FAILURE = ("There was an error with the Device Address API. "
                    "Please try again.")
GOODBYE = "Bye! Thanks for using the Sample Device Address API Skill!"
UNHANDLED = "This skill doesn't support that. Please ask something else"
HELP = ("You can use this skill by asking something like: "
        "whats my address?")


skill_name = "Is my subway screwed?"
help_text = ("You can say 1 train or B line to hear the subway status of that line.")

lines_slot_key = "lines"
lines_slot = "lines"

def runOnStartup():
    print("Session Started.")

    SOURCE = 'http://web.mta.info/status/ServiceStatusSubway.xml'
    response = requests.get(SOURCE)
    xml_string = response.text
    xml_dict = xmltodict.parse(xml_string)
    json_string = json.dumps(xml_dict)
    data = json.loads(json_string)

    subways = data['Siri']['ServiceDelivery']['SituationExchangeDelivery']['Situations']
    for index in range(len(subways['PtSituationElement'])):

        PtSituationElement = subways['PtSituationElement'][index]['Summary']
        print(PtSituationElement)
        if PtSituationElement.get('#text', False) != False:  # has a summary attribute
            summaryText = PtSituationElement['#text']
            print(summaryText)
            affectedSubways = subways['PtSituationElement'][index]['Affects']['VehicleJourneys'][
                'AffectedVehicleJourney']
            print(affectedSubways)
            # API returns a list if there are more than 1 affected lines
            if isinstance(affectedSubways, (list,)):
                for index2 in range(len(affectedSubways)):
                    print(affectedSubways[index2]['LineRef'])
                    line = affectedSubways[index2]['LineRef'].split()  # split MTA NYCT_3 w/ a space
                    line2 = line[1].split('_')  # split NYCT_3 with a _
                    line3 = line2[1]  # take the num array element
                    Subway_Status[line3.lower()] = summaryText
            else:
                print(affectedSubways['LineRef'])
                line = affectedSubways['LineRef'].split()
                line2 = line[1].split('_')
                line3 = line2[1]
                Subway_Status[line3.lower()] = summaryText

    # fill in blank values
    for key, value in Subway_Status.items():
        if Subway_Status[key] == '':
            Subway_Status[key] = 'You are good bro!'

    print(Subway_Status)


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """Handler for Skill Launch."""
    # type: (HandlerInput) -> Response
    runOnStartup()
    speech = "What subway line do you hope will arrive on time today?"

    handler_input.response_builder.speak(
        speech + " " + help_text).ask(help_text)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    """Handler for Help Intent."""
    # type: (HandlerInput) -> Response
    handler_input.response_builder.speak(help_text).ask(help_text)
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda handler_input:
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    """Single handler for Cancel and Stop Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "Goodbye!"

    return handler_input.response_builder.speak(speech_text).response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    """Handler for Session End."""
    # type: (HandlerInput) -> Response
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("subwayLines"))
def subwayLines(handler_input):
    """Check if a favorite color has already been recorded in
    session attributes. If yes, provide the color to the user.
    If not, ask for favorite color.
    """
    # type: (HandlerInput) -> Response
    train_value = handler_input.request_envelope.request.intent.slots['lines'].value
    if train_value.lower() in Subway_LIST:
        speech = Subway_Status[train_value.lower()]
    else:
        speech = "Thats not a valid subway line"

    handler_input.response_builder.speak(speech).ask("Do you want to check another line?")
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_intent_name("GetAddressIntent"))
def GetAddressIntent(handler_input):
    req_envelope = handler_input.request_envelope
    response_builder = handler_input.response_builder
    service_client_fact = handler_input.service_client_factory

    if not (req_envelope.context.system.user.permissions and
            req_envelope.context.system.user.permissions.consent_token):
        response_builder.speak(NOTIFY_MISSING_PERMISSIONS)
        response_builder.set_card(
            AskForPermissionsConsentCard(permissions=permissions))
        return response_builder.response

    try:
        device_id = req_envelope.context.system.device.device_id
        device_addr_client = service_client_fact.get_device_address_service()
        addr = device_addr_client.get_full_address(device_id)

        if addr.address_line1 is None and addr.state_or_region is None:
            response_builder.speak(NO_ADDRESS)
        else:
            response_builder.speak(ADDRESS_AVAILABLE.format(
                addr.address_line1, addr.state_or_region, addr.postal_code))
        return response_builder.response
    except ServiceException:
        response_builder.speak(ERROR)
        return response_builder.response
    except Exception as e:
        raise e


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    # type: (HandlerInput) -> Response
    speech = (
        "Say the subway line you need status on").format(skill_name)
    reprompt = ("You can say 1 train or B line")
    handler_input.response_builder.speak(speech).ask(reprompt)
    return handler_input.response_builder.response


def convert_speech_to_text(ssml_speech):
    """convert ssml speech to text, by removing html tags."""
    # type: (str) -> str
    s = SSMLStripper()
    s.feed(ssml_speech)
    return s.get_data()


@sb.global_response_interceptor()
def add_card(handler_input, response):
    """Add a card by translating ssml text to card content."""
    # type: (HandlerInput, Response) -> None
    response.card = SimpleCard(
        title=skill_name,
        content=convert_speech_to_text(response.output_speech.ssml))


@sb.global_response_interceptor()
def log_response(handler_input, response):
    """Log response from alexa service."""
    # type: (HandlerInput, Response) -> None
    print("Alexa Response: {}\n".format(response))


@sb.global_request_interceptor()
def log_request(handler_input):
    """Log request to alexa service."""
    # type: (HandlerInput) -> None
    print("Alexa Request: {}\n".format(handler_input.request_envelope.request))


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    # type: (HandlerInput, Exception) -> None
    print("Encountered following exception: {}".format(exception))

    speech = "Sorry, there was some problem. Please try again!!"
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response


######## Convert SSML to Card text ############
# This is for automatic conversion of ssml to text content on simple card
# You can create your own simple cards for each response, if this is not
# what you want to use.

from six import PY2
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser


class SSMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.full_str_list = []
        if not PY2:
            self.strict = False
            self.convert_charrefs = True

    def handle_data(self, d):
        self.full_str_list.append(d)

    def get_data(self):
        return ''.join(self.full_str_list)

################################################


# Handler to be provided in lambda console.
lambda_handler = sb.lambda_handler()