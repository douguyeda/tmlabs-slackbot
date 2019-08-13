"""
List of helper functions
"""
import os
import pickle
from google.oauth2 import service_account


def get_credentials():
    """ Get valid credentials from Google API """
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    creds = None
    token_path = os.path.abspath('token.pickle')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        credsFromEnv = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
        with open('credentials.json', 'w+') as f:
            f.write(credsFromEnv)
        creds = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds


def parse_cell(value):
    """ Ignore ASCII characters in case user entered them """
    return value.encode('ascii', 'ignore')
