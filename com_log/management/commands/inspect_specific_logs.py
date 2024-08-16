from django.core.management.base import BaseCommand
from com_log.models import CommunicationLog
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Inspect specific CommunicationLog entries'

    def handle(self, *args, **options):
        for log in CommunicationLog.objects.all():
            self.stdout.write(self.style.SUCCESS(f'Log ID: {log.id}'))
            self.stdout.write(f'Content Type: {log.content_type.model}')
            self.stdout.write(f'Object ID: {log.object_id}')
            self.stdout.write(f'Contact: {log.contact}')
            
            if log.contact:
                self.stdout.write(f'Contact class: {log.contact.__class__.__name__}')
                self.stdout.write('Contact attributes:')
                for field in log.contact._meta.fields:
                    value = getattr(log.contact, field.name)
                    self.stdout.write(f'  {field.name}: {value}')
            else:
                self.stdout.write('No associated contact')
            
            self.stdout.write(f'Communication Type: {log.communication_type}')
            self.stdout.write(f'Summary: {log.summary}')
            self.stdout.write('---')