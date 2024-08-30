from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_calendar_service(credentials_dict):
    credentials = Credentials(**credentials_dict)
    return build('calendar', 'v3', credentials=credentials)

def create_calendar_event(service, task):
    event = {
        'summary': task.title,
        'description': task.description,
        'start': {
            'date': task.due_date.isoformat(),
        },
        'end': {
            'date': task.due_date.isoformat(),
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event['id']
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def update_calendar_event(service, task):
    event = {
        'summary': task.title,
        'description': task.description,
        'start': {
            'date': task.due_date.isoformat(),
        },
        'end': {
            'date': task.due_date.isoformat(),
        },
    }

    try:
        service.events().update(
            calendarId='primary',
            eventId=task.google_calendar_event_id,
            body=event
        ).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')

def delete_calendar_event(service, event_id):
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')