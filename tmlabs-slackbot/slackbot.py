"""
Slackbot class which handles command from user
Author: Douglas Uyeda
Date: 02/19/2019
"""
from collections import OrderedDict
import constants
import spreadsheet
from helpers import parse_direction_mention


class Slackbot(object):
    """ Slackbot main class """

    def __init__(self, slack_client=None):
        self.slack_client = slack_client
        self.commands = OrderedDict([
            ("active", "Returns all active tests"),
            ("psupport", "Returns all active Product Support tests"),
            ("ife", "Returns all active IFE tests"),
            ("survey", "Returns all active Usabilla Surveys"),
            ("reload", "Returns all active tests which reload the page"),
            ("products", "Returns a list of products you can search by"),
            ("Search by product",
             "Type a product, such as 'rco' or 'dsco', to show all active tests on that product"),
            ("Search by EFEAT####",
             "Type in the EFEAT####, such as '5927', to bring up information about that test"),
            ("Search by recently launched",
             "Type in recent and day#, such as 'recent 7', to display all active tests launched in the past 7 days (max 120)"),
        ])
        self.default_response = "Beep Boop, here are a list of commands:\n" + \
            '\n'.join("%s = %r" % (key, val)
                      for (key, val) in self.commands.iteritems())
        self.invalid_response = constants.INVALID_QUERY_ENTERED
        self.products = ["co2", "dsco", "edp", "identity", "ln - edp",
                         "order detail", "rco", "tmr"]
        self.products_response = "Type any of the below products to search by!\n" + \
            "\n".join(self.products)
        self.doge = spreadsheet.get_doge()

    def connect(self):
        """ Connect to RTM feed """
        self.slack_client.rtm_connect(with_team_state=False)

    def parse_commands(self):
        """ Listen for messages and return the message and channel """
        for event in self.slack_client.rtm_read():
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = parse_direction_mention(event["text"])
                if user_id == self.slack_client:
                    return message, event["channel"]
        return None, None

    def handle_command(self, command):
        """ Execute command by calling Google Sheets API and returns query searched by user in the slack channel """
        command = command.lower()
        response = None
        if command.startswith("active"):
            response = spreadsheet.get_active_ab_tests()
        elif command.startswith("psupport"):
            response = spreadsheet.get_active_psupport()
        elif command == "ife":
            response = spreadsheet.get_active_by_index(4)
        elif command == "survey":
            response = spreadsheet.get_active_by_index(5)
        elif command.startswith("reload"):
            response = spreadsheet.get_active_by_index(6)
        elif command.startswith("products"):
            response = self.products_response
        elif command in self.products:
            response = spreadsheet.get_by_product(command)
        elif command.isdigit():
            response = spreadsheet.get_by_EFEAT(command)
        elif command.startswith("recent"):
            command = command.split()
            if len(command) != 2:
                return self.invalid_response
            response = spreadsheet.get_by_recent_days(command[1])
        elif command.startswith("doge") or command.startswith("wow"):
            response = self.doge
        return response

    def send_message(self, message, channel):
        """ Sends the response back to the channel """
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message or self.default_response
        )
