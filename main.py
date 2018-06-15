"""
Main slackbot program
Author: Douglas Uyeda
https://github.com/michaelkrukov/heroku-python-script
"""
import time
from slackbot import Slackbot
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient('xoxb-337102695590-V3oUU20y2t20t4lhz4Tc7MUC')
# 1 second delay between reading from RTM
RTM_READ_DELAY = 1

if __name__ == "__main__":
    slackbot = Slackbot(slack_client)
    slackbot.connect()
    print "Ticketmaster AB Bot connected!"
    while True:
        rtm_command, rtm_channel = slackbot.parse_commands()
        if rtm_command:
            response = slackbot.handle_command(rtm_command)
            slackbot.send_message(response, rtm_channel)
        time.sleep(RTM_READ_DELAY)
