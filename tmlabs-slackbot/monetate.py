"""
Grab data from the monetate metadata api here
"""
import os
import json
from collections import OrderedDict
from datetime import datetime, timedelta
import requests
import requests_cache
from constants import EXPERIENCE_SUMMARY_URL, INVALID_DAY_ENTERED, INVALID_EFEAT_ENTERED, NO_RESULTS_FOUND, MAX_DAYS
from helpers import create_external_link, format_date, get_monetate_auth_token


PAGE_SIZE = 150
SKIPPED_WORDS = ["A/A", "Companion", "[Goals]",
                 "Behavior", "Reporting", "[Sizing]", "[Demo]"]

DSCO_KEYWORDS = ['[dsco', '[discovery', '[ccp discovery']

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# cache results frome monetate metadata experience api
requests_cache.install_cache(
    os.path.join(__location__, "monetate_cache"), backend="sqlite", expire_after=600)


def get_experiences():
    """ Return a list of experiences from the monetate metadata api """
    auth_token = get_monetate_auth_token()
    experiences = requests.get(EXPERIENCE_SUMMARY_URL,
                               headers={
                                   "Authorization": "Token {}".format(auth_token)},
                               params={"account_domain": "ticketmaster.com", "page_size": PAGE_SIZE, "status": "active"}).json()

    results = []
    if experiences["meta"]["code"] > 400:
        print experiences["meta"]["errors"]
        return results

    # filter out unneeded experiences
    for exp in experiences["data"]:
        if not any(word in exp["experience_name"] for word in SKIPPED_WORDS):
            results.append(exp)

    return results


def get_active_ab_tests():
    """ Grab all active A/B tests """
    results = []
    experiences = get_experiences()
    for exp in experiences:
        experience_name = exp["experience_name"]
        experience_id = exp["id"]
        results.append(create_external_link(
            experience_name, experience_id) + " " + experience_name)

    if not results:
        return NO_RESULTS_FOUND
    return "\n".join(results)


def get_active_psupport():
    """ Returns all active prod support tests """
    results = []
    experiences = get_experiences()
    for exp in experiences:
        if len(exp["splits"]) == 1:
            experience_name = exp["experience_name"]
            results.append(create_external_link(
                experience_name, exp["id"]) + " " + experience_name)

    if not results:
        return NO_RESULTS_FOUND
    return "\n".join(results)


def get_active_by_product(product):
    """ Returns all active tests by product name """
    results = []
    experiences = get_experiences()

    if product == 'dsco':
        for exp in experiences:
            experience_name = exp["experience_name"]
            if any(word in experience_name.lower() for word in DSCO_KEYWORDS):
                results.append(create_external_link(
                    experience_name, exp["id"]) + " " + experience_name)

    else:
        product_search_string = "[" + product
        for exp in experiences:
            if product_search_string in experience_name.lower():
                results.append(create_external_link(
                    experience_name, exp["id"]) + " " + experience_name)

    if not results:
        return NO_RESULTS_FOUND
    return "\n".join(results)


def get_active_by_EFEAT(efeat_num):
    """ Return the details of a ticket by EFEAT#### """
    if len(efeat_num) != 4:
        return INVALID_EFEAT_ENTERED
    efeat_dict = OrderedDict()

    experiences = get_experiences()
    found = False
    for exp in experiences:
        experience_name = exp["experience_name"]
        if efeat_num in experience_name:
            found = True
            efeat_dict["Test Name"] = experience_name
            efeat_dict["Launch Date"] = format_date(exp["start_time"])
            efeat_dict["Link"] = create_external_link(
                experience_name, exp["id"])

    if found:
        return json.dumps(efeat_dict, indent=0)[2:-2]
    return NO_RESULTS_FOUND


def get_by_recent_days(days):
    """ Return all active tests launched in the past xx days """
    if not days.isdigit():
        return INVALID_DAY_ENTERED

    days = int(days)
    if days > 120:
        return MAX_DAYS

    experiences = get_experiences()
    days_offset = datetime.today() - timedelta(days=days)
    results = []

    for exp in experiences:
        launch_date = datetime.strptime(
            exp["start_time"], "%Y-%m-%dT%H:%M:%S.%fZ")
        experience_name = exp["experience_name"]
        if launch_date > days_offset:
            results.append(create_external_link(
                experience_name, exp["id"]) + " " + experience_name)

    if not results:
        return NO_RESULTS_FOUND
    return "\n".join(results)
