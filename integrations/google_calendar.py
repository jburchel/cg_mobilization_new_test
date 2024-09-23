from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .utils import check_and_refresh_credentials
import datetime
import logging

logger = logging.getLogger(__name__)

def get_calendar_service(request):
    logger.info("Creating Google Calendar service")
    credentials = check_and_refresh_credentials(request)
    if not credentials:
        logger.error("Failed to get valid credentials")
        return None
    return build('calendar', 'v3', credentials=credentials)

def create_calendar_event(request, task):
    logger.info(f"Attempting to create calendar event for task: {task.id}")
    try:
        service = get_calendar_service(request)
        if not service:
            logger.error("Failed to create Calendar service")
            return None

        reminder_minutes = get_reminder_minutes(task.reminder, task.custom_reminder)
        
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
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': reminder_minutes},
                ],
            },
        }
        
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        logger.info(f"Event created successfully. Event ID: {created_event['id']}")
        return created_event['id']
    except HttpError as e:
        logger.error(f"HttpError occurred while creating calendar event: {e.content}")
        logger.error(f"Error details: {e.error_details}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error occurred while creating calendar event: {str(e)}")
        return None

def update_calendar_event(request, task):
    logger.info(f"Attempting to update calendar event for task: {task.id}")
    try:
        service = get_calendar_service(request)
        if not service:
            logger.error("Failed to create Calendar service")
            return False

        reminder_minutes = get_reminder_minutes(task.reminder, task.custom_reminder)

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
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': reminder_minutes},
                ],
            },
        }

        updated_event = service.events().update(
            calendarId='primary',
            eventId=task.google_calendar_event_id,
            body=event
        ).execute()
        logger.info(f"Event updated successfully. Event ID: {updated_event['id']}")
        return True
    except HttpError as error:
        logger.error(f'An error occurred while updating the event: {error}')
        logger.error(f"Error details: {error.error_details}")
        return False

def delete_calendar_event(request, event_id):
    logger.info(f"Attempting to delete calendar event: {event_id}")
    try:
        service = get_calendar_service(request)
        if not service:
            logger.error("Failed to create Calendar service")
            return False

        service.events().delete(calendarId='primary', eventId=event_id).execute()
        logger.info(f"Event deleted successfully. Event ID: {event_id}")
        return True
    except HttpError as error:
        logger.error(f'An error occurred while deleting the event: {error}')
        logger.error(f"Error details: {error.error_details}")
        return False
    
def get_reminder_minutes(reminder_choice, custom_reminder):
    reminder_mapping = {
        '15_min': 15,
        '30_min': 30,
        '1_hour': 60,
        '2_hours': 120,
        '1_day': 1440,
        '1_week': 10080,
        'custom': custom_reminder
    }
    return reminder_mapping.get(reminder_choice, 30)  # Default to 30 minutes if not found