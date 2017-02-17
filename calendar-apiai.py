#!/usr/bin/env python

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") == "getCalendarEvents":
        res = getCalendarEvents()
        return res
    elif req.get("result").get("action") == "deleteCalendarEvent":
        res = deleteCalendarEvent()
        return res
    elif (req.get("result").get("action") == "rescheduleCalendarEvent" or req.get("result").get("action") == "rescheduleMeetingCK"):
        res = rescheduleCalendarEvent("MeetingCK")
        return res
    elif req.get("result").get("action") == "getDailyNews":
        res = getDailyNewsSummary()
        return res
    elif req.get("result").get("action") == "getNewsDetails":
        res = getNewsDetails("new US taxation law passed")
        return res
    elif req.get("result").get("action") == "getExperts":
        contexts = req.get("result").get("contexts")
        domainParameter = next((x for x in contexts if x.get("name") == "tax"), None)
        domain = domainParameter.get("name")
        res = getExperts(domain)
        return res
    elif req.get("result").get("action") == "scheduleMeeting":
        contexts = req.get("result").get("contexts")
        namesParameter = next((x for x in contexts if x.get("name") == "staffname"), None)
        names = namesParameter.get("parameters").get("names")
        res = scheduleMeeting(names)
        return res
    else:
        return {}

# TODO: Connect to Google API
def getCalendarEvents():
    speech = "You have the following appointments today. Risk Assessment Meeting at 2pm. Meeting CK at 630pm."

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "contextOut": [{"name":"RiskAssessmentMeeting", "parameters": { "time":"2pm"}},
        {"name":"MeetingCK", "parameters": {"time": "630pm"}}],
        "source": "g-buddy-apiai-calendar"
    }

# TODO: Connect to Google API
def deleteCalendarEvent():
    speech = "Calendar Event Deleted"

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "g-buddy-apiai-calendar"
    }

def rescheduleCalendarEvent(event):
    print("Rescheduling")
    speech = "Calendar event " + event + " reschedule to 11am tomorrow"

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "g-buddy-apiai-calendar"
    }

def getDailyNewsSummary():
    speech = "There are two high impact news today. For GIC, Amazon blah blah. For Asset Management, new US taxation law passed."

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "contextOut": [{"name":"newssummary", "parameters": { "GIC": "Amazon blah blah", "Asset Management": "new US taxation law passed" }}],
        "source": "g-buddy-apiai-calendar"
    }

def getNewsDetails(summary):
    if summary == "Amazon blah blah":
        speech = "Amazon blah blah. Blah blah blah"
    elif summary == "new US taxation law passed":
        speech = "US corp rate tax will be reduced by 10% while VAT is likely to increase."
    else:
        speech = "Sorry I can't get more details for " + summary

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "contextOut": [{ "name":"tax" }],
        "source": "g-buddy-apiai-news"
    }

def getExperts(domain):
    if domain == "tax":
        speech = "The experts on " + domain + " are Lennie and Allen"
    else:
        speech = "Sorry I can't find any experts for " + domain

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "contextOut": [{ "name":"staffname", "parameters": { "names": ["Lennie", "Allen"] }}],
        "source": "g-buddy-apiai-news"
    }

def scheduleMeeting(names):
    fullList = ""
    for name in names:
        fullList = name + " "

    speech = "Meeting scheduled for " + fullList + "tomorrw at 3pm to 4pm at 48M1"
    print("Response:")
    print(speech)

    return {
    "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "contextOut": [{ "name":"meeting", "parameters": { "invited": ["Lennie", "Allen"], "date": "2017-02-18", "startTime": "3pm", "endTime": "4pm", "venue":"48M1" }}],
        "source": "g-buddy-apiai-news"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
