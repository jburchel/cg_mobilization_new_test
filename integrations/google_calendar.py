from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
import datetime
import logging

logger = logging.getLogger(__name__)

def get_calendar_service(credentials_dict):
    credentials = Credentials(**credentials_dict)
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    return build('calendar', 'v3', credentials=credentials)

def create_calendar_event(service, task):
    event = {
        'summary': task.title,
        'description': task.description,
        'start': {
            'dateTime': task.due_date.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (task.due_date + datetime.timedelta(hours=1)).isoformat(),
            'timeZone': 'UTC',
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        logger.info(f"Event created: {event.get('htmlLink')}")
        return event['id']
    except HttpError as error:
        logger.error(f'An error occurred: {error}')
        return None

def update_calendar_event(service, task):
    event = {
        'summary': task.title,
        'description': task.description,
        'start': {
            'dateTime': task.due_date.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (task.due_date + datetime.timedelta(hours=1)).isoformat(),
            'timeZone': 'UTC',
        },
    }

    try:
        service.events().update(
            calendarId='primary',
            eventId=task.google_calendar_event_id,
            body=event
        ).execute()
        logger.info(f"Event updated: {task.google_calendar_event_id}")
    except HttpError as error:
        logger.error(f'An error occurred: {error}')

def delete_calendar_event(service, event_id):
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        logger.info(f"Event deleted: {event_id}")
    except HttpError as error:
        logger.error(f'An error occurred: {error}')