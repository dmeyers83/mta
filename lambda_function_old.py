# python standard library
import json
# third party
import requests
import xmltodict
#dataframe
import pandas as pd
#import library to strip html
from bs4 import BeautifulSoup


# ------------------------------Part1--------------------------------
# In this part we define a list that contains the player names, and
# a dictionary with player biographies
Subway_LIST = ["1", "2", "3", "4", "5", "6", "7", "a", "c", "e", "f", "b", "n", "r", "q", "m", "s", "j", "z", "d", "g","l"]

Subway_Status = {}


# ------------------------------Part2--------------------------------
# Here we define our Lambda function and configure what it does when
# an event with a Launch, Intent and Session End Requests are sent. # The Lambda function responses to an event carrying a particular
# Request are handled by functions such as on_launch(event) and
# intent_scheme(event).
def lambda_handler(event, context):
    if event['session']['new']:
        on_start()
    if event['request']['type'] == "LaunchRequest":
        print(event['context'])

        return on_launch(event)
    elif event['request']['type'] == "IntentRequest":
        return intent_scheme(event)
    elif event['request']['type'] == "SessionEndedRequest":
        return on_end()


# ------------------------------Part3--------------------------------
# Here we define the Request handler functions
def on_start():
    print("Session Started.")

    SOURCE = 'http://www.mta.info/status/serviceStatus.txt'
    response = requests.get(SOURCE)

    xml_string = response.text
    xml_dict = xmltodict.parse(xml_string)
    json_string = json.dumps(xml_dict)

    data = json.loads(json_string)

    subways = data['service']['subway']['line']

    df = pd.DataFrame.from_dict(subways)
    #df = df.drop(df.columns[0], axis=1)
    print (df)


    for i, row in df.iterrows():

        #strip out html of text
        subwayName = row['name']
        statusHtml = str(getattr(row, "text"))
        subwayDate = str(getattr(row, "Date"))
        subwayStatus = str(getattr(row, "status"))
        subwayTime = str(getattr(row, "Time"))


        statusNoHmtl = BeautifulSoup(statusHtml)
        updated_status = u' '.join(statusNoHmtl.findAll(text=True))
        df.at[i, 'text'] = updated_status

        #break out subway lines: ACE -> ' A C E', ' A or C or E', 'A', 'B'
        print(subwayName)
        if len(subwayName) > 1 and subwayName != 'SIR':
            subwayLetters = list(subwayName)
            print(subwayLetters)
            for letter in subwayLetters:
                df = df.append({'name': letter.lower(), 'text': updated_status, 'Date': subwayDate, 'Time': subwayTime, 'status': subwayStatus}, ignore_index=True)

    for i, row in df.iterrows():
        subwayName = row['name']
        statusText = str(getattr(row, "text"))
        subwayDate = str(getattr(row, "Date"))
        subwayStatus = str(getattr(row, "status"))
        subwayTime = str(getattr(row, "Time"))

        #add brackets to look for subway name in text
        letterBrackets = '[' +subwayName.upper() + ']'

        #return true if status has the letter
        textStatusHasLetter = letterBrackets in statusText

        #return good if either there are no status issues, or the status text doesn't contain the letter
        if subwayStatus == "GOOD SERVICE" or textStatusHasLetter == False :
            Subway_Status[subwayName] = 'You are good bro!'
        else:
            Subway_Status[subwayName] = statusText
    print(Subway_Status)


def on_launch(event):
    onlunch_MSG = "What subway line do you hope will arrive on time today?"
    reprompt_MSG = "Do you want to know if your subway will actually come on time?"
    card_TEXT = "Pick a subway line"
    card_TITLE = "Choose a subway line"
    return output_json_builder_with_reprompt_and_card(onlunch_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)


def on_end():
    print("Session Ended.")


# -----------------------------Part3.1-------------------------------
# The intent_scheme(event) function handles the Intent Request.
# Since we have a few different intents in our skill, we need to
# configure what this function will do upon receiving a particular
# intent. This can be done by introducing the functions which handle
# each of the intents.
def intent_scheme(event):
    intent_name = event['request']['intent']['name']

    if intent_name == "subwayLines":
        return subway_line(event)
    elif intent_name in ["AMAZON.NoIntent", "AMAZON.StopIntent", "AMAZON.CancelIntent"]:
        return stop_the_skill(event)
    elif intent_name == "AMAZON.HelpIntent":
        return assistance(event)
    elif intent_name == "AMAZON.FallbackIntent":
        return fallback_call(event)


# ---------------------------Part3.1.1-------------------------------
# Here we define the intent handler functions
def subway_line(event):
    name = str(event['request']['intent']['slots']['lines']['value'])
    subway_list_lower = [w.lower() for w in Subway_LIST]
    if name.lower() in subway_list_lower:
        reprompt_MSG = "Do you want the status on another subway line?"
        card_TEXT = "You've picked " + name.lower()
        card_TITLE = Subway_Status[name.lower()]
        return output_json_builder_with_reprompt_and_card(Subway_Status[name.lower()], card_TEXT, card_TITLE,
                                                          reprompt_MSG, False)
    else:
        wrongname_MSG = "I cannot recongize that line.  Do you want to try again?"
        reprompt_MSG = "Try again?"
        card_TEXT = "Try again."
        card_TITLE = "Wrong line name."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)


def stop_the_skill(event):
    stop_MSG = "Thank you. Bye!"
    reprompt_MSG = ""
    card_TEXT = "Bye."
    card_TITLE = "Bye Bye."
    return output_json_builder_with_reprompt_and_card(stop_MSG, card_TEXT, card_TITLE, reprompt_MSG, True)


def assistance(event):
    assistance_MSG = "You can choose among these subway lines: " + ', '.join(
        map(str, Subway_LIST))
    reprompt_MSG = "Do you want to get status of a MTA subway line?"
    card_TEXT = "You've asked for help."
    card_TITLE = "Help"
    return output_json_builder_with_reprompt_and_card(assistance_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)


def fallback_call(event):
    fallback_MSG = "I can't help you with that, try rephrasing the question or ask for help by saying HELP."
    reprompt_MSG = "Do you want to hear the status of another subwayline"
    card_TEXT = "You've asked a wrong question."
    card_TITLE = "Wrong question."
    return output_json_builder_with_reprompt_and_card(fallback_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)


# ------------------------------Part4--------------------------------
# The response of our Lambda function should be in a json format.
# That is why in this part of the code we define the functions which
# will build the response in the requested format. These functions
# are used by both the intent handlers and the request handlers to
# build the output.

def plain_text_builder(text_body):
    text_dict = {}
    text_dict['type'] = 'PlainText'
    text_dict['text'] = text_body
    return text_dict


def reprompt_builder(repr_text):
    reprompt_dict = {}
    reprompt_dict['outputSpeech'] = plain_text_builder(repr_text)
    return reprompt_dict


def card_builder(c_text, c_title):
    card_dict = {}
    card_dict['type'] = "Simple"
    card_dict['title'] = c_title
    card_dict['content'] = c_text
    return card_dict


def response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value):
    speech_dict = {}
    speech_dict['outputSpeech'] = plain_text_builder(outputSpeach_text)
    speech_dict['card'] = card_builder(card_text, card_title)
    speech_dict['reprompt'] = reprompt_builder(reprompt_text)
    speech_dict['shouldEndSession'] = value
    return speech_dict


def output_json_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value):
    response_dict = {}
    response_dict['version'] = '1.0'
    response_dict['response'] = response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title,
                                                                              reprompt_text, value)
    return response_dict