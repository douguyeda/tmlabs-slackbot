"""Example Usabilla for Apps"""
import os
import usabilla as ub
from constants import EFEAT, USABILLA_URL


def is_active_survey(survey):
    """ determines if a survey is active or not """
    return survey["status"] == "active" and EFEAT in survey["name"]


def get_active_surveys():
    """ grab all active EFEAT surveys """

    usabilla_access_key = os.environ["USABILLA_ACCESS_KEY"]
    usabilla_secret_key = os.environ["USABILLA_SECRET_KEY"]

    try:
        api = ub.APIClient(usabilla_access_key, usabilla_secret_key)
        campaigns = api.get_resource(
            api.SCOPE_LIVE, api.PRODUCT_WEBSITES, api.RESOURCE_CAMPAIGN)
        surveys = campaigns["items"]

        output = []
        for survey in surveys:
            if is_active_survey(survey):
                output.append("{0}{1} {2}".format(
                    USABILLA_URL, survey["id"], survey["name"]))
        return "\n".join(output)

    except Exception as e:
        return e.message
