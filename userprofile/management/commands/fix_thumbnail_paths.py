from django.core.management.base import BaseCommand
from userprofile.models import CustomUser
import os

class Command(BaseCommand):
    help = 'Fix incorrect thumbnail paths in the database'

    def handle(self, *args, **kwargs):
        for user in CustomUser.objects.all():
            if user.profile_thumbnail:
                old_path = user.profile_thumbnail.name
                new_path = os.path.basename(old_path)
                if old_path != new_path:
                    user.profile_thumbnail.name = new_path
                    user.save(update_fields=['profile_thumbnail'])
                    self.stdout.write(self.style.SUCCESS(f"Corrected path for user {user.username}: {new_path}"))
