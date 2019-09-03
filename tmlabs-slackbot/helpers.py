"""
List of helper functions
"""
import os
import re
import json
import pickle
from google.oauth2 import service_account

MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def get_credentials():
    """ Get valid credentials from Google API """
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    creds = None
    token_path = os.path.abspath('token.pickle')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, grab from config file
    if not creds or not creds.valid:
        service_account_info = json.loads(
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
        creds = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds


def parse_direction_mention(message_text):
    """
    Finds a direct mention (a mention that is at the beginning) in message text
    and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    if matches:
        return(matches.group(1), matches.group(2).strip())
    return (None, None)


def parse_cell(value):
    """ Ignore ASCII characters in case user entered them """
    return value.encode('ascii', 'ignore')
