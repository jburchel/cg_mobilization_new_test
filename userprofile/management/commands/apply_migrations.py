from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Applies all migrations for the userprofile app'

    def handle(self, *args, **options):
        call_command('migrate', 'userprofile')
        self.stdout.write(self.style.SUCCESS('Successfully applied migrations for userprofile'))