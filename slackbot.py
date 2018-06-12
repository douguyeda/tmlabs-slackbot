"""
Main slackbot program
Author: Douglas Uyeda
https://github.com/michaelkrukov/heroku-python-script
"""
import time
from collections import OrderedDict
from slackclient import SlackClient
from spreadsheet import get_active_tests, get_active_psupport, get_active_ccp, get_active_reload, get_by_page_type, get_by_EFEAT, get_by_SIMA

# instantiate Slack client
slack_client = SlackClient('xoxb-337102695590-V3oUU20y2t20t4lhz4Tc7MUC')
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM

def get_doge():
    """ wow """
    filehandle = open("doge.txt", "r")
    return filehandle.read()

def parse_bot_commands(slack_events):
    """
    Listens for input from the user
    returns:
        (Command, Channel which contains command)
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            return event["text"], event["channel"]
    return None, None


def handle_command(command, channel):
    """ Execute command by calling Google Sheets API and returns query searched by user in the slack channel """

    commands = OrderedDict()
    commands["active"] = "Returns all active tests"
    commands["product"] = "Returns all active Product Support Tests"
    commands["ccp"] = "Returns all active CCP tests"
    commands["reload"] = "Returns all tests that cause the page to reload"
    commands["pagetypes"] = "Returns a list of page types you can search by"
    commands["Search by page type"] = "Type a page type such as 'ADP' or 'RCO' to show all active tests on that page type"
    commands["Search by EFEAT####"] = "Type the EFEAT#### such as '5927' to bring up information about that test"
    commands["Search by analyst first mame"] = "Type in analyst first name to find all active tests tagged to that analyst"

    # List of page types to search by
    pagetypes = ["adp", "ccp edp", "confirmation", "discovery", "home", "identity", "mobile app", "rco", "srp", "tmr checkout"]
    pagetypes_response = "Type any of the below page types to search by!\n" + "\n".join(pagetypes)

    # List of analysts to search by
    analysts = ["randy", "glen", "amber", "lily", "danielle", "michelle", "christine"]

    default_response = "Beep Boop, here are a list of commands:\n" + '\n'.join("%s = %r" % (key, val) for (key, val) in commands.iteritems())
    command = command.lower()

    response = None
    if command.startswith("active"):
        response = get_active_tests()
    elif command.startswith("product"):
        response = get_active_psupport()
    elif command == "ccp":
        response = get_active_ccp()
    elif command.startswith("reload"):
        response = get_active_reload()
    elif command.startswith("pagetypes"):
        response = pagetypes_response
    elif command in pagetypes:
        response = get_by_page_type(command)
    elif command.isdigit():
        response = get_by_EFEAT(command)
    elif command in analysts:
        response = get_by_SIMA(command)
    elif command.startswith("doge") or command.startswith("wow"):
        response = get_doge()

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print "AB Bot connected and running!"
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            rtm_command, rtm_channel = parse_bot_commands(slack_client.rtm_read())
            if rtm_command:
                handle_command(rtm_command, rtm_channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print "Connection failed. Exception traceback printed above."
