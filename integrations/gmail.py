from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from .utils import check_and_refresh_credentials
import base64
import logging

logger = logging.getLogger(__name__)

def get_gmail_service(request):
    logger.info("Creating Gmail service")
    credentials = check_and_refresh_credentials(request)
    if not credentials:
        logger.error("Failed to get valid credentials")
        return None
    return build('gmail', 'v1', credentials=credentials)

def send_email(service, to, subject, body):
    try:
        message = create_message('me', to, subject, body)
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        logger.info(f'Message Id: {sent_message["id"]}')
        return sent_message
    except HttpError as error:
        logger.error(f'An error occurred: {error}')
        return None

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8'))
    return {'raw': raw_message.decode('utf-8')}

def send_task_email(request, task):
    logger.info(f"Attempting to send email for task {task.id}")
    try:
        service = get_gmail_service(request)
        if not service:
            logger.error("Failed to create Gmail service")
            return False

        to = request.user.email
        if not to:
            logger.error("User email not set")
            return False

        subject = f"New Task: {task.title}"
        body = f"A new task has been created:\n\nTitle: {task.title}\nDescription: {task.description}\nDue Date: {task.due_date}\n\nPlease check your task tracker for more details."

        sent_message = send_email(service, to, subject, body)
        if sent_message:
            logger.info(f"Email sent successfully for task {task.id}")
            return True
        else:
            logger.error(f"Failed to send email for task {task.id}")
            return False
    except Exception as e:
        logger.exception(f"Error sending email for task {task.id}: {str(e)}")
        return False