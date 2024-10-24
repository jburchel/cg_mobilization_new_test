from django.core.management.base import BaseCommand
from userprofile.models import CustomUser

class Command(BaseCommand):
    help = 'Fix incorrect thumbnail paths in the database'

    def handle(self, *args, **kwargs):
        for user in CustomUser.objects.all():
            if user.profile_thumbnail and 'profile_thumbnails/profile_thumbnails/' in user.profile_thumbnail.name:
                corrected_path = user.profile_thumbnail.name.replace('profile_thumbnails/profile_thumbnails/', 'profile_thumbnails/')
                user.profile_thumbnail.name = corrected_path
                user.save(update_fields=['profile_thumbnail'])
                self.stdout.write(self.style.SUCCESS(f"Corrected path for user {user.username}: {corrected_path}"))
