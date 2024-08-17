from django.core.management.base import BaseCommand
from contacts.models import Church, People
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class Command(BaseCommand):
    help = 'Resets the sample data by deleting all Churches and People'

    def handle(self, *args, **kwargs):
        # Delete all Churches
        Church.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All Churches have been deleted'))

        # Delete all People
        People.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All People have been deleted'))

        # Optionally, delete all Users except superusers
        CustomUser.objects.exclude(is_superuser=True).delete()
        self.stdout.write(self.style.SUCCESS('All non-superuser Users have been deleted'))

        self.stdout.write(self.style.SUCCESS('Sample data has been reset successfully'))