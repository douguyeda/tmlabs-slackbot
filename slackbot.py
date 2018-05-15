"""
Main slackbot program
Author: Douglas Uyeda
https://github.com/michaelkrukov/heroku-python-script
"""
import time
from collections import OrderedDict
from slackclient import SlackClient
from spreadsheet import get_active_tests, get_active_psupport, get_active_ccp, get_active_reload, get_by_product, get_by_EFEAT

# instantiate Slack client
slack_client = SlackClient('xoxb-337102695590-V3oUU20y2t20t4lhz4Tc7MUC')
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM

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
    """
    Execute the command by calling Google Sheets API
    returns:
        query searched by user in the slack channel
    """
    commands = OrderedDict()
    commands["active"] = "Returns all active tests"
    commands["product"] = "Returns all active Product Support Tests"
    commands["ccp"] = "Returns all active CCP EDP tests"
    commands["reload"] = "Returns all tests that cause the page to reload"
    commands["Search by page type"] = "Type a page type such as 'ADP' to show all active tests on that page type"
    commands["Search by EFEAT####"] = "Type the EFEAT#### such as '5927' to bring up information about that test"

    products = ["adp", "home", "rco", "identity", "tmr checkout", "discovery", "mobile app"]

    default_response = "Beep Boop, here are a list of commands:\n" + '\n'.join("%s = %s" % (key, val) for (key, val) in commands.iteritems())
    command = command.lower()

    response = None
    if command.startswith("active"):
        response = get_active_tests()
    elif command.startswith("product"):
        response = get_active_psupport()
    elif command.startswith("ccp"):
        response = get_active_ccp()
    elif command.startswith("reload"):
        response= get_active_reload()
    elif command in products:
        response = get_by_product(command)
    elif command.isdigit():
        response = get_by_EFEAT(command)

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
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print "Connection failed. Exception traceback printed above."
