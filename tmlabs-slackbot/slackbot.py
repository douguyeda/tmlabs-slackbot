"""
Slackbot class which handles command from user
Author: Douglas Uyeda
"""
import json
from constants import INVALID_QUERY_ENTERED
from monetate import get_active_ab_tests, get_active_psupport, get_active_by_product, get_active_by_EFEAT, get_by_recent_days
from usabilla_query import get_active_surveys
from helpers import parse_direction_mention, get_doge

SLACKBOT_ID = "U9X30LFHC"

COMMANDS = {
    "active": "Returns all active tests",
    "psupport": "Returns all active Product Support tests",
    "usabilla": "Returns all active Usabilla Surveys",
    "products": "Returns a list of products you can search by",
    "Search by product": "Type a product, such as 'rco' or 'dsco', to show all active tests on that product",
    "Search by EFEAT####": "Type in the EFEAT####, such as '5927', to bring up information about that test",
    "Search by recently launched": "Type in recent and day#, such as 'recent 7', to display all active tests launched in the past 7 days (max 120)"
}

PRODUCTS = ["apps", "co2", "dsco", "edp", "post-purchase", "rco"]


class Slackbot(object):
    """ Slackbot main class """

    def __init__(self, slack_client=None):
        self.slack_client = slack_client
        self.default_response = "Sorry, I did not recognize that.  Here are a list of commands:\n" + \
            json.dumps(COMMANDS, indent=0)[2:-2]
        self.products_response = "Type any of the below products to search by!\n" + \
            "\n".join(PRODUCTS)

    def connect(self):
        """ Connect to RTM feed """
        self.slack_client.rtm_connect(with_team_state=False)

    def parse_commands(self):
        """ Listen for messages and return the message and channel """
        for event in self.slack_client.rtm_read():
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = parse_direction_mention(event["text"])
                if user_id == SLACKBOT_ID:
                    return message, event["channel"]
        return None, None

    def handle_command(self, command):
        """ Execute command by calling Google Sheets API and returns query searched by user in the slack channel """
        command = command.lower()
        response = None
        if command.startswith("active"):
            response = get_active_ab_tests()
        elif command.startswith("psupport"):
            response = get_active_psupport()
        elif command == "usabilla":
            response = get_active_surveys()
        elif command.startswith("products"):
            response = self.products_response
        elif command in PRODUCTS:
            response = get_active_by_product(command)
        elif command.isdigit():
            response = get_active_by_EFEAT(command)
        elif command.startswith("recent"):
            command = command.split()
            if len(command) != 2:
                return INVALID_QUERY_ENTERED
            response = get_by_recent_days(command[1])
        elif command.startswith("doge") or command.startswith("wow"):
            response = get_doge()
        return response

    def send_message(self, message, channel):
        """ Sends the response back to the channel """
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message or self.default_response
        )
