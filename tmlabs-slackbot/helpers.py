"""
List of helper functions
"""
import os
import time
import re
import pickle
from datetime import datetime
import requests
import jwt
from constants import EFEAT, JIRA_LINK, MONETATE_LINK

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
REFRESH_URL = "https://api.monetate.net/api/auth/v0/refresh/"


def get_monetate_auth_token():
    """ Grab Monetate Auth Token """
    creds = None
    token_path = os.path.join(__location__, "monetate_token.pickle")
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
            if datetime.now() < datetime.fromtimestamp(creds["data"]["expires_at"]):
                return creds["data"]["token"]

    private_key = os.environ["MONETATE_PRIVATE_KEY"]
    payload = jwt.encode({
        "username": "api-735-douglasuyeda",
        "iat": int(time.time())
    }, private_key, algorithm="RS256")
    authorization = "JWT {}".format(payload)
    creds = requests.get(REFRESH_URL, headers={
        "Authorization": authorization}).json()
    with open(token_path, "wb") as token:
        pickle.dump(creds, token)

    return creds["data"]["token"]


def create_external_link(experience_name, experience_id):
    """ create jira link from experience name """
    if EFEAT in experience_name:
        index = experience_name.find(EFEAT)
        return JIRA_LINK + EFEAT + "-" + experience_name[index+5: index+9]
    return MONETATE_LINK + str(experience_id)


def format_date(date_str):
    """ format experience summary api date to mm/dd/yyyy"""
    no_time = date_str[:10]
    formatted = datetime.strptime(no_time, '%Y-%m-%d')
    return formatted.strftime("%m/%d/%Y")


def parse_direction_mention(message_text):
    """
    Finds a direct mention (a mention that is at the beginning) in message text
    and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    if matches:
        return(matches.group(1), matches.group(2).strip())
    return (None, None)


def get_doge():
    """ wow """
    return ":doge2:"
