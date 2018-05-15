"""
Main slackbot program
Author: Douglas Uyeda
https://github.com/michaelkrukov/heroku-python-script
"""
import time
from slackclient import SlackClient
from spreadsheet import get_active_tests, get_active_psupport, get_active_ccp, get_by_EFEAT, get_by_product

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
    commands = {
        "active":"Displays all active tests",
        "product": "Displays all active Product Support Tests",
        "ccp": "Displays all active CCP EDP tests",
        "product id": "Displays all active tests by product id (ADP, HOME, RCO, identity)",
        "EFEAT####": "Displays information about an EFEAT (Please type only the #)."
    }
    default_response = "Beep Boop, here are a list of commands:\n" + '\n'.join("%s=%r" % (key,val) for (key,val) in commands.iteritems())

    command = command.lower()

    response = None
    if command.startswith("active"):
        response = get_active_tests()
    elif command.startswith("product"):
        response = get_active_psupport()
    elif command.startswith("ccp"):
        response = get_active_ccp()
    elif command == "adp" or "home" or "rco" or "identity" or "tmr checkout":
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
