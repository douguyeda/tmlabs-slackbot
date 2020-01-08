"""
Slackbot class which handles command from user
Author: Douglas Uyeda
Date: 02/19/2019
"""
from constants import INVALID_QUERY_ENTERED
import monetate
from usabilla_query import get_active_surveys
from helpers import parse_direction_mention, get_doge
from commands import COMMANDS, PRODUCTS

SLACKBOT_ID = "U9X30LFHC"


class Slackbot(object):
    """ Slackbot main class """

    def __init__(self, slack_client=None):
        self.slack_client = slack_client
        self.default_response = "Beep Boop, here are a list of commands:\n" + \
            '\n'.join("%s = %r" % (key, val)
                      for (key, val) in COMMANDS.iteritems())
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
            response = monetate.get_active_ab_tests()
        elif command.startswith("psupport"):
            response = monetate.get_active_psupport()
        elif command == "usabilla":
            response = get_active_surveys()
        elif command.startswith("products"):
            response = self.products_response
        elif command in PRODUCTS:
            response = monetate.get_active_by_product(command)
        elif command.isdigit():
            response = monetate.get_active_by_EFEAT(command)
        elif command.startswith("recent"):
            command = command.split()
            if len(command) != 2:
                return INVALID_QUERY_ENTERED
            response = monetate.get_by_recent_days(command[1])
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
