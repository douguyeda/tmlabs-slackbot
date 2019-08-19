# Ticketmaster AB Bot

TM Labs slackbot which returns information about active A/B tests.
More information can be found here: https://confluence.livenation.com/display/ECOM/TM+Labs+Slackbot

### Prerequisites

- python 2.7
- pip
- Google API credentials, generated from `Service Account Key` option
- Bot User OAuth Access token from Slack API

### Installing

1.  Open a terminal, and navigate to the root of the project
2.  Type `pip install -r requirements.txt` to install dependencies
3.  Save your google api credentials as an environment variable with variable name `GOOGLE_APPLICATION_CREDENTIALS`
4.  Save your slackbot token as an environment variable with variable name `SLACK_BOT_TOKEN`
5.  Save your Usabilla access key as an environment variable with variable name `USABILLA_ACCESS_KEY`
6.  Save your Usabilla secret key as an environment variable with variable name `USABILLA_SECRET_KEY`
7.  To run the program, type `python main.py`

### Authors

Douglas Uyeda

### License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
