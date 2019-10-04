"""
List of helper functions
"""
import os
import re
import json
from google.oauth2 import service_account
from constants import JIRA_LINK

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def get_credentials():
    """ Get valid credentials from Google API """
    service_account_info = json.loads(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    creds = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES)
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


def is_active_test(row):
    """ determines if an AB test is active if row 9 has an 'X' """
    return row[9] == "x"


def parse_cell(value):
    """ Ignore ASCII characters in case user entered them """
    return value.encode('ascii', 'ignore')


def format_row_result(row):
    """ Formats the result from reading google sheet """
    return "{0}{1} {2}".format(
        JIRA_LINK, row[0], parse_cell(row[1]))


def get_doge():
    """ wow """
    path = os.path.abspath('doge.txt')
    if os.path.exists(path):
        filehandle = open(path, "r")
        return filehandle.read()
    return "wow, very slackbot"
