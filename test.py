from collections import OrderedDict
import json

commands = OrderedDict()
commands["active"] = "Returns all active tests"
commands["product"] = "Returns all active Product Support Tests"
commands["ccp"] = "Returns all active CCP EDP tests"
commands["reload"] = "Returns all tests that cause the page to reload"
commands["Search by page type"] = "Type a page type such as 'ADP' to show all active tests on that page type"
commands["Search by EFEAT####"] = "Type the EFEAT#### such as '5927' to bring up information about that test"

default_response = "Beep Boop, here are a list of commands:\n" + '\n'.join("%s = %s" % (key,val) for (key,val) in commands.iteritems())

print default_response