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

def get_active_tests():
    """ Grab all active tests from the A/B active sheet """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http, cache_discovery=False,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1yhqjAVuo_nlByP4G6zGfQ3gF3fz3IR4FXnqaN93OVUo'
    rangeName = 'AB - Tests Live!A2:J'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    active_tests = []
    if not values:
        return "No values found in spreadsheet"
    else:
        for row in values:
            try:
                if row[9] == "x":
                    active_tests.append("https://contegixapp1.livenation.com/jira/browse/" + row[0] + " " + row[1])
            except IndexError:
                pass
    return 'All active tests:\n' + '\n'.join(active_tests)

def get_active_psupport():
    """ Grab all active Product support tests from the A/B active sheet """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, cache_discovery=False, discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1yhqjAVuo_nlByP4G6zGfQ3gF3fz3IR4FXnqaN93OVUo'
    rangeName = 'AB - Prod Support!A2:F'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    active_psupport = []
    if not values:
        return "No values found in spreadsheet"
    else:
        for row in values:
            try:
                if row[5] == "x":
                    active_psupport.append("https://contegixapp1.livenation.com/jira/browse/" + row[0] + " " + row[1])
            except IndexError:
                pass
    return 'All active product support tests:\n' + '\n'.join(active_psupport)

def get_active_ccp():
    """ Grab all active CCP EDP tests from the A/B active sheet """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, cache_discovery=False, discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1yhqjAVuo_nlByP4G6zGfQ3gF3fz3IR4FXnqaN93OVUo'
    rangeName = 'AB - Tests Live!A2:J'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    active_ccp = []
    if not values:
        return "No values found in spreadsheet"
    else:
        for row in values:
            try:
                if row[5] == "x" and row[9] == "x":
                    active_ccp.append("https://contegixapp1.livenation.com/jira/browse/" + row[0] + " " + row[1])
            except IndexError:
                pass
    return 'All active CCP EDP tests:\n' + '\n'.join(active_ccp)

def get_by_EFEAT(efeat_num):
    """ Grab the details of a ticket by EFEAT# """
    # quick check to see if valid EFEAT# has been entered
    if(len(efeat_num) != 4):
        return "Invalid EFEAT# entered: " + efeat_num
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, cache_discovery=False, discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1yhqjAVuo_nlByP4G6zGfQ3gF3fz3IR4FXnqaN93OVUo'
    rangeName = 'AB - Tests Live!A2:L'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    efeat = OrderedDict()
    efeat_string = "EFEAT-" + efeat_num
    found = False
    if not values:
        return "No values found in spreadsheet"
    else:
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

def get_by_product(product):
    """ Grab active tests by product value from the A/B active sheet """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, cache_discovery=False, discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1yhqjAVuo_nlByP4G6zGfQ3gF3fz3IR4FXnqaN93OVUo'
    rangeName = 'AB - Tests Live!A2:K'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    active_product = []
    if not values:
        return "No values found in spreadsheet"
    else:
        for row in values:
            try:
                if row[9] == "x" and row[10].lower() == product:
                    active_product.append("https://contegixapp1.livenation.com/jira/browse/" + row[0] + " " + row[1])
            except IndexError:
                pass

    if not active_product:
        return 'No tests found with product: ' + product
    return 'All active ' + product + ' tests:\n' + '\n'.join(active_product)
