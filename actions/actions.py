# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, AllSlotsReset

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
import os.path
import pdb

from datetime import datetime, timedelta
from dateutil import tz

SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'cred.json'

class getEvent(Action):

    def name(self) -> Text:
        return "action_get_event"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        event_name_list, date = get_event()
        response_text = "Got events for {}:\n".format(date)
        for i in event_name_list:
            response_text += "{} ({} - {})\n".format(i["summary"], i["start"], i["end"])
        dispatcher.utter_message(text=response_text)
        return []

def get_calendar_service():
   creds = None
   # The file token.pickle stores the user's access and refresh tokens, and is
   # created automatically when the authorization flow completes for the first
   # time.
   if os.path.exists('token.pickle'):
       with open('token.pickle', 'rb') as token:
           creds = pickle.load(token)
   # If there are no (valid) credentials available, let the user log in.
   if not creds or not creds.valid:
       if creds and creds.expired and creds.refresh_token:
           creds.refresh(Request())
       else:
           flow = InstalledAppFlow.from_client_secrets_file(
               CREDENTIALS_FILE, SCOPES)
           creds = flow.run_local_server(port=0)

       # Save the credentials for the next run
       with open('token.pickle', 'wb') as token:
           pickle.dump(creds, token)

   service = build('calendar', 'v3', credentials=creds)
   return service

def get_event():

    service = get_calendar_service() 
    now = datetime.utcnow().isoformat() + 'Z'
    today = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day)    
    end = (start + timedelta(1)).isoformat() + 'Z'
    events = service.events().list( calendarId='primary', timeMin=now, timeMax=end,
       maxResults=10, singleEvents=True,
       orderBy='startTime').execute().get("items",[])
    events_list = []
    for i in events:
        events_list.append({"summary": i["summary"], "start": datetime.strptime(i["start"]["dateTime"], "%Y-%m-%dT%H:%M:%S+05:30").strftime("%H:%M"), "end": datetime.strptime(i["end"]["dateTime"], "%Y-%m-%dT%H:%M:%S+05:30").strftime("%H:%M")})
    print(events_list)    
    return events_list, datetime.strptime(events[0]["start"]["dateTime"], "%Y-%m-%dT%H:%M:%S+05:30").strftime("%d/%m/%Y")

#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
