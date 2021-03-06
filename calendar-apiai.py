#!/usr/bin/env python

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import json
import os
from datetime import datetime as dt

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

event1 = {
    "subject": "Data Analytics Project Meeting",
    "date": "2017-02-18",
    "startTime": "14:00:00",
    "endTime": "15:00:00",
    "attendees": ["Michael", "Heather"],
    "venue": "Meeting Room 5"
}
event2 = {
    "subject": "Meeting Boss",
    "date": "2017-02-18",
    "startTime": "19:00:00",
    "endTime": "20:00:00",
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
        # contexts = req.get("result").get("contexts")
        # namesParameter = next((x for x in contexts if x.get("name") == "staffname"), None)
        date = req.get("result").get("parameters").get("date")
        startTime = req.get("result").get("parameters").get("time")
        duration = req.get("result").get("parameters").get("duration")
        names = req.get("result").get("parameters").get("names")
        res = scheduleMeeting(date, startTime, duration, names)
        return res
    elif req.get("result").get("action") == "scheduleMeetingAuto":
        contexts = req.get("result").get("contexts")
        namesParameter = next((x for x in contexts if x.get("name") == "staffname"), None)
        names = namesParameter.get("parameters").get("names")
        duration = namesParameter.get("parameters").get("duration.original")
        res = scheduleMeetingAuto(names, duration)
        return res
    elif req.get("result").get("action") == "getTaxExposure":
        source = req.get("originalRequest").get("source")
        res = getTaxExposure(source)
        return res
    else:
        return {}

def timeToStr(timeValue):
    date_obj = dt.strptime(timeValue, '%H:%M:%S')
    return dt.strftime(date_obj, '%I %p')

# TODO: Connect to Google API
def getCalendarEvents():
    print("Getting calendar events")

    eventsResponse = ""
    for e in eventsToday:


        eventsResponse = eventsResponse + e["subject"] + " at " + timeToStr(e["startTime"]) + " to " + timeToStr(e["endTime"]) + " at " + e["venue"] + " with " + " and ".join(e["attendees"]) + ". "
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

def getTaxExposure(source):
    if source == "google":
        speech = "I know you are currently using a voice channel for this conversation. It will be easier to read the numbers on Slack."
    else:
        speech = 'Shares: US$1,688,888\nOptions: US$3,333,888\n(Gosh, this sounds like the TOTO Hongbao jackpot!!!)'
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        "contextOut": [],
        "source": "g-buddy-apiai-tax"
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
            speech = "Sorry but I cannot find any events having attendees " + " and ".join(attendees) + " to reschedule"
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
    speech = "There are two high impact news today. First, for developed markets, new US taxation law passed. Second, for emerging markets, Brazil is finally out of recession. "

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
        speech = "After 2 years, Brazil is finally out of recession. GDP grew by 1.4%. Manufacturing sector leads the recovery by a 5% gain. "
    elif summary == "new US taxation law passed":
        speech = "A new taxation law was passed by the US Senate earlier today. US corporate tax rate will be reduced by up to 10% in the coming years, while consumer tax is likely to increase. "
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

def scheduleMeeting(date, time, duration, names):
    speech = "Ok, booked meeting with " + " and ".join(names) + " tomorrow at " + time + " for " + duration + ". Venue is Meeting Room 2."

    print("Response:")
    print(speech)

    return {
    "speech": speech,
        "displayText": speech,
        # "data": data,
        "contextOut": [],
        "source": "g-buddy-apiai-calendar"
    }

def scheduleMeetingAuto(names, duration):
    speech = "Ok, booked meeting with " + " and ".join(names) + " tomorrow at 11AM for " + duration + ". Venue is Meeting Room 9."

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "contextOut": [],
        "source": "g-buddy-apiai-calendar"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
