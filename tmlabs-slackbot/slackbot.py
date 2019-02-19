"""
Slackbot class which handles command from user
Author: Douglas Uyeda
Date: 02/19/2019
"""
from collections import OrderedDict
from spreadsheet import get_active_ab_tests, get_active_psupport, get_active_by_index, get_by_product, get_by_EFEAT, get_by_recent, get_by_quarter, get_doge

class Slackbot(object):
    """ Slackbot main class """
    def __init__(self, slack_client=None):
        self.slack_client = slack_client
        self.commands = OrderedDict([
            ("active", "Returns all active tests"),
            ("psupport", "Returns all active Product Support tests"),
            ("ccp", "Returns all active CCP tests"),
            ("ife", "Returns all active IFE tests"),
            ("reload", "Returns all active tests which reload the page"),
            ("products", "Returns a list of products you can search by"),
            ("Search by product", "Type a product, such as 'RCO' or 'Discovery', to show all active tests on that product"),
            ("Search by EFEAT####", "Type in the EFEAT####, such as '5927', to bring up information about that test"),
            ("Search by recently launched", "Type in recent and day#, such as 'recent 7', to display all active tests launched in the past 7 days (max 120)"),
            ("Search by quarter", "Type in the quarter and year, such as 'q1 2018', to pull all launched tests in that range")
        ])
        self.default_response = "Beep Boop, here are a list of commands:\n" + '\n'.join("%s = %r" % (key, val) for (key, val) in self.commands.iteritems())
        self.invalid_response = "Invalid query entered"
        self.products = ["ccp edp", "confirmation", "discovery", "identity", "mobile app", "order detail", "rco", "survey", "tmr checkout"]
        self.products_response = "Type any of the below products to search by!\n" + "\n".join(self.products)
        self.doge = get_doge()

    def connect(self):
        """ Connect to RTM feed """
        self.slack_client.rtm_connect(with_team_state=False)

    def parse_commands(self):
        """ Listen for messages and return the message and channel """
        for event in self.slack_client.rtm_read():
            if event["type"] == "message" and not "subtype" in event:
                return event["text"], event["channel"]
        return None, None

    def handle_command(self, command):
        """ Execute command by calling Google Sheets API and returns query searched by user in the slack channel """
        command = command.lower()
        response = None
        if command.startswith("active"):
            response = get_active_ab_tests()
        elif command.startswith("psupport"):
            response = get_active_psupport()
        elif command == "ccp":
            response = get_active_by_index(5)
        elif command == "ife":
            response = get_active_by_index(4)
        elif command.startswith("reload"):
            response = get_active_by_index(6)
        elif command.startswith("products"):
            response = self.products_response
        elif command in self.products:
            response = get_by_product(command)
        elif command.isdigit():
            response = get_by_EFEAT(command)
        elif command.startswith("recent"):
            command = command.split()
            if len(command) != 2:
                return self.invalid_response
            response = get_by_recent(command[1])
        elif command.startswith("q"):
            command = command.split()
            if len(command) != 2:
                return self.invalid_response
            response = get_by_quarter(command[0], command[1])
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
