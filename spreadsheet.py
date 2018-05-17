"""
Google Sheets API Calls Go Here
Author: Douglas Uyeda
'cache_discovery=False' removes ghsheets error
https://stackoverflow.com/questions/40154672/importerror-file-cache-is-unavailable-when-using-python-client-for-google-ser
"""
import json
from collections import OrderedDict
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery

def get_credentials():
    """ Get valid credentials to use """
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    return creds

def get_tests():
    """ Grab all the values from AB - Tests Live sheet """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http, cache_discovery=False,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1yhqjAVuo_nlByP4G6zGfQ3gF3fz3IR4FXnqaN93OVUo'
    rangeName = 'AB - Tests Live!A2:M'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        return "No values found in spreadsheet"
    return values

def get_product_tests():
    """ Grab all the values from AB - Prod support sheet  """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, cache_discovery=False, discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1yhqjAVuo_nlByP4G6zGfQ3gF3fz3IR4FXnqaN93OVUo'
    rangeName = 'AB - Prod Support!A2:M'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        return "No values found in spreadsheet"
    return values

def get_active_tests():
    """ Return all active tests """
    values = get_tests()
    active_tests = []
    for row in values:
        try:
            if row[9] == "x":
                active_tests.append("https://contegixapp1.livenation.com/jira/browse/" + row[0] + " " + row[1])
        except IndexError:
            pass
            
    if not active_tests:
        return "No active tests found"
    return 'All active tests:\n' + '\n'.join(active_tests)

def get_active_psupport():
    """ Return all active product support tests """
    values = get_product_tests()
    active_psupport = []
    for row in values:
        try:
            if row[9] == "x":
                active_psupport.append("https://contegixapp1.livenation.com/jira/browse/" + row[0] + " " + row[1])
        except IndexError:
            pass

    if not active_psupport:
        return "No active product support tests found"
    return 'All active product support tests:\n' + '\n'.join(active_psupport)

def get_active_ccp():
    """ Return all active ccp tests """
    values = get_tests()
    active_ccp = []
    for row in values:
        try:
            if row[5] == "x" and row[9] == "x":
                active_ccp.append("https://contegixapp1.livenation.com/jira/browse/" + row[0] + " " + row[1])
        except IndexError:
            pass

    if not active_ccp:
        return "No active ccp tests found"
    return 'All active CCP EDP tests:\n' + '\n'.join(active_ccp)

def get_active_reload():
    """ Return all active tests that force a reload """
    values = get_tests()
    active_reload = []
    for row in values:
        try:
            if row[6] == "x" and row[9] == "x":
                active_reload.append("https://contegixapp1.livenation.com/jira/browse/" + row[0] + " " + row[1])
        except IndexError:
            pass

    if not active_reload:
        return "No active reload tests found "
    return 'All active reload tests:\n' + '\n'.join(active_reload)

def get_by_page_type(page_type):
    """ Return all active tests by page type from the A/B active sheet """
    values = get_tests()
    active_page = []
    for row in values:
        try:
            if row[9] == "x" and row[10].lower() == page_type:
                active_page.append("https://contegixapp1.livenation.com/jira/browse/" + row[0] + " " + row[1])
        except IndexError:
            pass

    if not active_page:
        return 'No tests found with page type: ' + page_type
    return 'All active ' + page_type + ' tests:\n' + '\n'.join(active_page)

def get_by_EFEAT(efeat_num):
    """ Return the details of a ticket by EFEAT#### """
    # quick check to see if valid EFEAT# has been entered
    if(len(efeat_num) != 4):
        return "Invalid EFEAT# entered: " + efeat_num

    efeat = OrderedDict()
    efeat_string = "EFEAT-" + efeat_num
    found = False

    values = get_tests()
    for row in values:
        try:
            if row[0] == efeat_string:
                found = True
                efeat["Test Name"] = efeat_string + " " + row[1]
                efeat["Hypothesis"] = row[3]
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
