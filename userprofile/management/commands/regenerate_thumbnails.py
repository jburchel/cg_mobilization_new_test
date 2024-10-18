from django.core.management.base import BaseCommand
from userprofile.models import CustomUser

class Command(BaseCommand):
    help = 'Regenerates thumbnails for all users'

    def handle(self, *args, **options):
        users = CustomUser.objects.all()
        for user in users:
            if user.profile_image:
                user.create_thumbnail()
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully regenerated thumbnail for user {user.username}'))
