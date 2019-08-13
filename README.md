# Ticketmaster AB Bot

TM Labs slackbot which returns information about active A/B tests.
More information can be found here: https://confluence.livenation.com/display/ECOM/TM+Labs+Slackbot

### Prerequisites

- python 2.7
- pip
- Google API credentials, generated from `Service Account Key` option
- Bot User OAuth Access token from Slack API

### Installing

1.  Please save the following as environment variables:
    1.  Google API Credentials - `GOOGLE_APPLICATION_CREDENTIALS` : `your value`
    2.  Slack API Bot User OAuth Access token - `SLACK_BOT_TOKEN` : `your value`
2.  Open a terminal and navigate to the root of the project
3.  Type `pip install -r requirements.txt` to install dependencies
4.  To run the program, type `python main.py`

### Authors

Douglas Uyeda

### License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
