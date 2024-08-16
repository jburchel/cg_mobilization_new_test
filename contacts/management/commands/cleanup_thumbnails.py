from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps
from django.db.models import ImageField
import os

class Command(BaseCommand):
    help = 'Cleans up unused thumbnails and orphaned images'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        
        # Get all models with ImageFields
        image_fields = []
        for model in apps.get_models():
            image_fields.extend(
                (f.name, model) for f in model._meta.fields if isinstance(f, ImageField)
            )
        
        # Get all image paths from the database
        db_images = set()
        for field_name, model in image_fields:
            for instance in model.objects.all():
                image = getattr(instance, field_name)
                if image:
                    db_images.add(image.name)
        
        # Clean up unused images and thumbnails
        for root, dirs, files in os.walk(media_root):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, media_root)
                
                if relative_path not in db_images:
                    if file.endswith('_thumb.jpg'):
                        # This is a thumbnail, remove it
                        os.remove(file_path)
                        self.stdout.write(self.style.SUCCESS(f'Removed unused thumbnail: {relative_path}'))
                    elif not any(db_image.startswith(relative_path) for db_image in db_images):
                        # This is not a thumbnail and not referenced in the database, remove it
                        os.remove(file_path)
                        self.stdout.write(self.style.SUCCESS(f'Removed orphaned image: {relative_path}'))
        
        self.stdout.write(self.style.SUCCESS('Cleanup completed'))