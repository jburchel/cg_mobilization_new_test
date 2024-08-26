# clear_com_log.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from com_log.models import ComLog

class Command(BaseCommand):
    help = 'Clears the communication log'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            help='Delete records older than specified number of days',
        )

    def handle(self, *args, **options):
        days = options['days']

        with transaction.atomic():
            if days:
                cutoff_date = timezone.now() - timezone.timedelta(days=days)
                deleted_count = ComLog.objects.filter(date__lt=cutoff_date).delete()[0]
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted {deleted_count} com log entries older than {days} days')
                )
            else:
                deleted_count = ComLog.objects.all().delete()[0]
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted all {deleted_count} com log entries')
                )