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

event1 = {
    "subject": "Risk Assessment Meeting",
    "date": "2017-02-18",
    "startTime": "14:00:00",
    "endTime": "15:00:00",
    "attendees": ["Alice", "Bob", "Charlie"],
    "venue": "Meeting Room 123"
}
event2 = {
    "subject": "Meeting Boss",
    "date": "2017-02-18",
    "startTime": "18:30:00",
    "endTime": "19:30:00",
    "attendees": ["Vincent Cheang Weng Seng"],
    "venue": "Boss's Office"
}
event3 = {
    "subject": "Meeting with JPM",
    "date": "2017-02-19",
    "startTime": "09:00:00",
    "endTime": "10:00:00",
    "attendees": ["Denny", "Emily"],
    "venue": "Meeting Room 321"
}

events = [event1, event2, event3]
eventsToday = [event1, event2]

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
        startTime = req.get("result").get("parameters").get("time")
        attendees = req.get("result").get("parameters").get("names")
        venue = req.get("result").get("parameters").get("venue")
        res = rescheduleCalendarEvent(startTime, venue, attendees, None)
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
    print("Getting calendar events")

    eventsResponse = ""
    for e in eventsToday:
        eventsResponse = eventsResponse + e["subject"] + " at " + e["startTime"] + " to " + e["endTime"] + " at " + e["venue"] + " with " + " ".join(e["attendees"]) + ". "
    speech = "You have the following appointments today. " + eventsResponse

    print("Response:")
    print(speech)

    # eventsJson = json.dumps([e.__dict__ for e in eventsToday])
    # print(eventsJson)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        "contextOut": [{"name":"events", "parameters": { "meetings": eventsToday } }],
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

def rescheduleCalendarEvent(startTime, venue, attendees, subject):
    print("Rescheduling event")
    if startTime != "":
        result = [ event for event in eventsToday if event["startTime"] == startTime ]
        if len(result) >= 1:
            speech = "Calendar event " + result[0]["subject"] + " has been rescheduled to 11am tomorrow. Venue is changed to Meeting Room 2."
            rescheduledEvent = result[0]
        else:
            speech = "Sorry but I cannot find any events starting at " + startTime + " to reschedule"
            rescheduledEvent = None
    elif attendees is not None and len(attendees) > 0:
        result = [ e for e in eventsToday if set(attendees) == set(e["attendees"]) ]
        if len(result) >= 1:
            speech = "Calendar event " + result[0]["subject"] + " has been rescheduled to 3pm tomorrow. Venue is unchanged."
            rescheduledEvent = result[0]
        else:
            speech = "Sorry but I cannot find any events having attendees " + " ".join(attendees) + " to reschedule"
            rescheduledEvent = None
    else:
        speech = "Sorry. Reschedule by subject or venue has not yet been implemented."
        rescheduledEvent = None

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        "contextOut": [{"name":"event-rescheduled", "parameters": rescheduledEvent }],
        "source": "g-buddy-apiai-calendar"
    }

def getDailyNewsSummary():
    speech = "There are two high impact news today. First, for developed markets, new US taxation law passed. For emerging markets, Brazil is finally out of recession. "

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [{"name":"newssummary", "parameters": {}}],
        "source": "g-buddy-apiai-calendar"
    }

def getNewsDetails(summary):
    if summary == "Brazil":
        speech = "After 2 years, Brazil is finally out of recession. GDP grew by 1.4%. Manufacturing sector leads the recovery by a 5% gain. For details, please click on the link in your Google Now."
    elif summary == "new US taxation law passed":
        speech = "A new taxation law is passed by the US Senate. US corp rate tax will be reduced by up to 10% in the coming years, while consumer tax is likely to increase. For details, please click on the link in your Google Now."
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
        speech = "The experts on " + domain + " are Lenny and Alan"
    else:
        speech = "Sorry I can't find any experts for " + domain

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "contextOut": [{ "name":"staffname", "parameters": { "names": ["Lenny", "Alan"] }}],
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
