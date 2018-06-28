"""
Google Sheets API Calls Go Here
Author: Douglas Uyeda
'cache_discovery=False' removes ghsheets error
https://stackoverflow.com/questions/40154672/importerror-file-cache-is-unavailable-when-using-python-client-for-google-ser
"""
import os
import json
from collections import OrderedDict
from datetime import datetime, timedelta
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery

def get_credentials():
    """ Get valid credentials to use """
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    credentials_raw = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    service_account_info = json.loads(credentials_raw)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    return creds

def build_sheet(range_name):
    """ Build a google sheet by choosing a sheet and the range """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, cache_discovery=False,
                              discoveryServiceUrl=discoveryUrl)
    spreadsheetId = "1yhqjAVuo_nlByP4G6zGfQ3gF3fz3IR4FXnqaN93OVUo"
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        return "No values found in spreadsheet"
    return values

def get_all_tests():
    """ Combine tests live and prod support sheet """
    active = build_sheet("AB - Tests Live!A2:M")
    product = build_sheet("AB - Prod Support!A2:M")
    return active + product

def get_active_tests():
    """ Return all active tests """
    values = build_sheet("AB - Tests Live!A2:J")
    active_tests = []
    for row in values:
        try:
            if row[9] == "x":
                active_tests.append("https://contegixapp1.livenation.com/jira/browse/{0} {1}".format(row[0], row[1]))
        except IndexError:
            pass

    if not active_tests:
        return "No active tests found"
    return 'All active tests:\n' + '\n'.join(active_tests)

def get_active_psupport():
    """ Return all active product support tests """
    values = build_sheet("AB - Prod Support!A2:J")
    active_psupport = []
    for row in values:
        try:
            if row[9] == "x":
                active_psupport.append("https://contegixapp1.livenation.com/jira/browse/{0} {1}".format(row[0], row[1]))
        except IndexError:
            pass

    if not active_psupport:
        return "No active product support tests found"
    return 'All active product support tests:\n' + '\n'.join(active_psupport)

def get_active_ccp():
    """ Return all active ccp tests """
    merged_list = get_all_tests()
    active_ccp = []
    for row in merged_list:
        try:
            if row[5] == "x" and row[9] == "x":
                active_ccp.append("https://contegixapp1.livenation.com/jira/browse/{0} {1}".format(row[0], row[1]))
        except IndexError:
            pass

    if not active_ccp:
        return "No active ccp tests found"
    return 'All active CCP tests:\n' + '\n'.join(active_ccp)

def get_active_reload():
    """ Return all active tests that force a reload """
    merged_list = get_all_tests()
    active_reload = []
    for row in merged_list:
        try:
            if row[6] == "x" and row[9] == "x":
                active_reload.append("https://contegixapp1.livenation.com/jira/browse/{0} {1}".format(row[0], row[1]))
        except IndexError:
            pass

    if not active_reload:
        return "No active reload tests found "
    return 'All active reload tests:\n' + '\n'.join(active_reload)

def get_by_page_type(page_type):
    """ Return all active tests by page type from the A/B active sheet """
    merged_list = get_all_tests()
    active_page = []
    for row in merged_list:
        try:
            if row[9] == "x" and row[10].lower() == page_type:
                active_page.append("https://contegixapp1.livenation.com/jira/browse/{0} {1}".format(row[0], row[1]))
        except IndexError:
            pass

    if not active_page:
        return 'No active tests found with page type: ' + page_type
    return "All active {0} tests\n{1}".format(page_type, '\n'.join(active_page))

def get_by_EFEAT(efeat_num):
    """ Return the details of a ticket by EFEAT#### """
    # quick check to see if valid EFEAT# has been entered
    if len(efeat_num) != 4:
        return "Invalid EFEAT# entered.  Please make sure the EFEAT# is 4 digits long"

    efeat = OrderedDict()
    efeat_string = "EFEAT-" + efeat_num
    found = False

    merged_list = get_all_tests()
    for row in merged_list:
        try:
            if efeat_string in row:
                found = True
                efeat["Test Name"] = efeat_string + " " + row[1]
                efeat["Hypothesis"] = row[3].replace("\n", ", ")
                efeat["Launch Date"] = row[7]
                efeat["Link"] = "https://contegixapp1.livenation.com/jira/browse/" + row[0]
                if row[9] == "x":
                    efeat["Active"] = "yes"
                efeat["Product Leads"] = row[11].replace("\n", ", ")
                break
        except IndexError:
            efeat["Active"] = "no"

    if found is False:
        return efeat_string + " not found"
    return json.dumps(efeat, indent=0)[2:-2]

def get_by_recent(days):
    """ Return all active tests launched in the past xx days """
    if not days.isdigit():
        return "Invalid day passed.  Make sure you entered an integer"

    days = int(days)
    if days > 30:
        return "Max amount of days is 30.  Please try entering a number less than 30."

    merged_list = get_all_tests()
    days_offset = datetime.today() - timedelta(days=days)
    recent_tests = []

    for row in merged_list:
        try:
            launch_date = datetime.strptime(row[7], '%m/%d/%Y')
            if row[9] == "x" and launch_date > days_offset:
                recent_tests.append("{0} https://contegixapp1.livenation.com/jira/browse/{1} {2}".format(row[7], row[0], row[1]))
        except IndexError:
            pass

    if not recent_tests:
        return "No active tests launched in the past {0} days".format(days)
    return "All active tests launched in the past {0} days:\n{1}".format(days, '\n'.join(recent_tests))

def get_doge():
    """ wow """
    filehandle = open("doge.txt", "r")
    return filehandle.read()
