from django.core.management.base import BaseCommand
from contacts.models import Church, People
from com_log.models import CommunicationLog
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        # Create sample churches
        church1 = Church.objects.create(church_name="First Baptist Church")
        church2 = Church.objects.create(church_name="St. Mary's Catholic Church")
        self.stdout.write(self.style.SUCCESS(f'Created churches: {church1}, {church2}'))

        # Create sample people
        person1 = People.objects.create(first_name="John", last_name="Doe")
        person2 = People.objects.create(first_name="Jane", last_name="Smith")
        self.stdout.write(self.style.SUCCESS(f'Created people: {person1}, {person2}'))

        # Create sample communication logs
        log1 = CommunicationLog.objects.create(
            content_type=ContentType.objects.get_for_model(Church),
            object_id=church1.id,
            communication_type='email',
            summary="Discussed upcoming event"
        )
        log2 = CommunicationLog.objects.create(
            content_type=ContentType.objects.get_for_model(People),
            object_id=person1.id,
            communication_type='phone',
            summary="Followed up on donation"
        )
        self.stdout.write(self.style.SUCCESS(f'Created communication logs: {log1}, {log2}'))

        self.stdout.write(self.style.SUCCESS('Sample data created successfully'))