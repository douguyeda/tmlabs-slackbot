"""
Google Sheets API Calls Go Here
Author: Douglas Uyeda
'cache_discovery=False' removes ghsheets error
https://stackoverflow.com/questions/40154672/importerror-file-cache-is-unavailable-when-using-python-client-for-google-ser
"""
import json
from collections import OrderedDict
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import constants
from helpers import get_credentials, parse_cell


def build_sheet(name, column_start, column_end):
    """ Build google sheet by name, start column, and end column """
    sheet_range = "{0}!{1}:{2}".format(name, column_start, column_end)
    service = build('sheets', 'v4', credentials=get_credentials(),
                    cache_discovery=False)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=constants.AB_TESTS_SHEET_ID,
                                range=sheet_range).execute()
    values = result.get('values', [])
    if not values:
        return constants.NO_RESULTS_FOUND
    return values


def get_all_tests():
    """ Combine tests live and prod support sheet """
    active = build_sheet(constants.AB_TESTS_LIVE, "A2", "K")
    product = build_sheet(constants.AB_TESTS_PROD_SUPPORT, "A2", "K")
    return active + product


def get_active_ab_tests():
    """ Return all active AB tests """
    values = build_sheet(constants.AB_TESTS_LIVE, "A2", "J")
    results = []
    for row in values:
        try:
            if row[9] == "x":
                results.append("{0}{1} {2}".format(
                    constants.JIRA_LINK, row[0], parse_cell(row[1])))
        except IndexError:
            pass
    if not results:
        return constants.NO_RESULTS_FOUND
    return '\n'.join(results)


def get_active_psupport():
    """ Return all active product support tests """
    values = build_sheet(constants.AB_TESTS_PROD_SUPPORT, "A2", "J")
    results = []
    for row in values:
        try:
            if row[9] == "x":
                results.append("{0}{1} {2}".format(
                    constants.JIRA_LINK, row[0], parse_cell(row[1])))
        except IndexError:
            pass

    if not results:
        return constants.NO_RESULTS_FOUND
    return '\n'.join(results)


def get_active_by_index(row_num):
    """ Grab all active tests by row number """
    tests = get_all_tests() if row_num == 6 else build_sheet(
        constants.AB_TESTS_LIVE, "A2", "J")
    results = []
    for row in tests:
        try:
            if row[row_num] == "x" and row[9] == "x":
                results.append("{0}{1} {2}".format(
                    constants.JIRA_LINK, row[0], parse_cell(row[1])))
        except IndexError:
            pass

    if not results:
        return constants.NO_RESULTS_FOUND
    return '\n'.join(results)


def get_by_product(product):
    """ Return all active tests by product """
    all_tests = get_all_tests()
    results = []
    for row in all_tests:
        try:
            if row[9] == "x" and row[10].lower() == product:
                results.append("{0}{1} {2}".format(
                    constants.JIRA_LINK, row[0], parse_cell(row[1])))
        except IndexError:
            pass

    if not results:
        return constants.NO_RESULTS_FOUND
    return '\n'.join(results)


def get_by_EFEAT(efeat_num):
    """ Return the details of a ticket by EFEAT#### """
    if len(efeat_num) != 4:
        return constants.INVALID_EFEAT_ENTERED

    efeat = OrderedDict()
    efeat_string = "EFEAT-" + efeat_num
    found = False

    all_tests = get_all_tests()
    for row in all_tests:
        try:
            if efeat_string in row:
                found = True
                efeat["Test Name"] = efeat_string + " " + parse_cell(row[1])
                efeat["Hypothesis"] = parse_cell(row[3]).replace("\n", ", ")
                efeat["Launch Date"] = row[7]
                efeat["Link"] = "{}{}".format(constants.JIRA_LINK, row[0])
                if row[9] == "x":
                    efeat["Active"] = "yes"
                break
        except IndexError:
            efeat["Active"] = "no"

    if found is False:
        return constants.NO_RESULTS_FOUND
    return json.dumps(efeat, indent=0)[2:-2]


def get_by_recent_days(days):
    """ Return all active tests launched in the past xx days """
    if not days.isdigit():
        return constants.INVALID_DAY_ENTERED

    days = int(days)
    if days > 120:
        return constants.MAX_DAYS

    all_tests = get_all_tests()
    days_offset = datetime.today() - timedelta(days=days)
    results = []

    for row in all_tests:
        try:
            launch_date = datetime.strptime(row[7], '%m/%d/%Y')
            if row[9] == "x" and launch_date > days_offset:
                results.append("{0} {1}{2} {3}".format(
                    row[7], constants.JIRA_LINK, row[0], parse_cell(row[1])))

        except (IndexError, ValueError):
            pass

    if not results:
        return constants.NO_RESULTS_FOUND
    return '\n'.join(results)


def get_doge():
    """ wow """
    filehandle = open("tmlabs-slackbot/doge.txt", "r")
    return filehandle.read()
