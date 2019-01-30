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

ROW_MAP = {
    4: 'IFE',
    5: 'CCP',
    6: 'Reload'
}

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
    active = build_sheet("AB - Tests Live!A2:J")
    product = build_sheet("AB - Prod Support!A2:J")
    return active + product

def get_active_ab_tests():
    """ Return all active AB tests """
    values = build_sheet("AB - Tests Live!A2:J")
    results = []
    for row in values:
        try:
            if row[9] == "x":
                results.append("https://contegixapp1.livenation.com/jira/browse/{0} {1}".format(row[0], row[1]))
        except IndexError:
            pass

    if not results:
        return "No active AB tests found"
    return 'All active AB tests:\n' + '\n'.join(results)

def get_active_psupport():
    """ Return all active product support tests """
    values = build_sheet("AB - Prod Support!A2:J")
    results = []
    for row in values:
        try:
            if row[9] == "x":
                results.append("https://contegixapp1.livenation.com/jira/browse/{0} {1}".format(row[0], row[1]))
        except IndexError:
            pass

    if not results:
        return "No active product support tests found"
    return 'All active product support tests:\n' + '\n'.join(results)

def get_active_by_index(row_num):
    """ Grab all active tests by row number """
    tests = build_sheet("AB - Tests Live!A2:J") if row_num == 4 else get_all_tests()
    results = []
    for row in tests:
        try:
            if row[row_num] == "x" and row[9] == "x":
                results.append("https://contegixapp1.livenation.com/jira/browse/{0} {1}".format(row[0], row[1]))
        except IndexError:
            pass

    row_name = ROW_MAP[row_num]
    if not results:
        return "No active " + row_name + "tests found"
    return "All active " + row_name + " tests" + ":\n" + "\n".join(results)

def get_by_product(product):
    """ Return all active tests by product """
    all_tests = get_all_tests()
    results = []
    for row in all_tests:
        try:
            if row[9] == "x" and row[10].lower() == product:
                results.append("https://contegixapp1.livenation.com/jira/browse/{0} {1}".format(row[0], row[1]))
        except IndexError:
            pass

    if not results:
        return 'No active tests found on product: ' + product
    return "All active {0} tests\n{1}".format(product, '\n'.join(results))

def get_by_EFEAT(efeat_num):
    """ Return the details of a ticket by EFEAT#### """
    if len(efeat_num) != 4:
        return "Invalid EFEAT# entered.  Please make sure the EFEAT# is 4 digits long"

    efeat = OrderedDict()
    efeat_string = "EFEAT-" + efeat_num
    found = False

    all_tests = get_all_tests()
    for row in all_tests:
        try:
            if efeat_string in row:
                found = True
                efeat["Test Name"] = efeat_string + " " + row[1]
                efeat["Hypothesis"] = row[3].replace("\n", ", ")
                efeat["Launch Date"] = row[7]
                efeat["Link"] = "https://contegixapp1.livenation.com/jira/browse/" + row[0]
                if row[9] == "x":
                    efeat["Active"] = "yes"
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
    if days > 120:
        return "Max amount of days is 120.  Please try entering a number less than 120."

    all_tests = get_all_tests()
    days_offset = datetime.today() - timedelta(days=days)
    results = []

    for row in all_tests:
        try:
            if row[7] == '':
                pass
            launch_date = datetime.strptime(row[7], '%m/%d/%Y')
            if row[9] == "x" and launch_date > days_offset:
                results.append("{0} https://contegixapp1.livenation.com/jira/browse/{1} {2}".format(row[7], row[0], row[1]))
        except IndexError:
            pass

    if not results:
        return "No active tests launched in the past {0} days".format(days)
    return "All active tests launched in the past {0} days:\n{1}".format(days, '\n'.join(results))

def get_by_quarter(qtr, year):
    """ Returns all active tests launched in a Quarter range """
    quarters = {
        "q1": ["1/1", "3/31"],
        "q2": ["4/1", "6/30"],
        "q3": ["7/1", "9/30"],
        "q4": ["10/1", "12/31"]
    }
    if qtr not in quarters:
        return "Invalid quarter entered, try 'q1', 'q2', 'q3', or 'q4'"
    if not year.isdigit():
        return "Invalid year entered"

    start_string = quarters[qtr][0] + "/" + year
    end_string = quarters[qtr][1] + "/" + year
    start_date = datetime.strptime(start_string, '%m/%d/%Y')
    end_date = datetime.strptime(end_string, '%m/%d/%Y')

    all_tests = get_all_tests()
    quarter_tests = []
    for row in all_tests:
        try:
            if row[7] == '':
                pass
            launch_date = datetime.strptime(row[7], '%m/%d/%Y')
            if start_date <= launch_date <= end_date:
                quarter_tests.append("https://contegixapp1.livenation.com/jira/browse/{0} {1}".format(row[0], row[1]))
        except IndexError:
            pass

    if not quarter_tests:
        return "No tests found in {0} {1}".format(qtr, year)
    return "All tests launched in {0} {1}:\n{2}".format(qtr, year, '\n'.join(quarter_tests))


def get_doge():
    """ wow """
    filehandle = open("tmlabs-slackbot/doge.txt", "r")
    return filehandle.read()
