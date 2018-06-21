"""
Main slackbot program
Author: Douglas Uyeda
https://github.com/michaelkrukov/heroku-python-script
"""
import os
import time
from slackclient import SlackClient
from slackbot import Slackbot

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# 1 second delay between reading from RTM
RTM_READ_DELAY = 1

if __name__ == "__main__":
    slackbot = Slackbot(slack_client)
    slackbot.connect()
    print "TM Labs AB Bot connected!"
    while True:
        rtm_command, rtm_channel = slackbot.parse_commands()
        if rtm_command:
            response = slackbot.handle_command(rtm_command)
            slackbot.send_message(response, rtm_channel)
        time.sleep(RTM_READ_DELAY)
