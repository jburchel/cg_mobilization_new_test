import os
import logging
from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    profile_thumbnail = models.ImageField(upload_to='profile_thumbnails/', null=True, blank=True)
    
    def has_profile_image(self):
        return bool(self.profile_image and self.profile_image.name)

    def has_profile_thumbnail(self):
        return bool(self.profile_thumbnail and self.profile_thumbnail.name)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_image = None if is_new else CustomUser.objects.get(pk=self.pk).profile_image
        
        super().save(*args, **kwargs)
        
        if is_new or (self.profile_image and self.profile_image != old_image):
            self.create_thumbnail()

    def create_thumbnail(self):
        if not self.profile_image:
            return

        logger.info(f"Creating thumbnail for user {self.username}")
        try:
            # Delete old thumbnail if it exists
            if self.profile_thumbnail:
                default_storage.delete(self.profile_thumbnail.path)

            img = Image.open(self.profile_image.path)
            img.thumbnail((32, 32))
            thumb_name, thumb_extension = os.path.splitext(self.profile_image.name)
            thumb_extension = thumb_extension.lower()
            thumb_filename = f"{self.pk}_thumb{thumb_extension}"

            if thumb_extension in ['.jpg', '.jpeg']:
                FTYPE = 'JPEG'
            elif thumb_extension == '.gif':
                FTYPE = 'GIF'
            elif thumb_extension == '.png':
                FTYPE = 'PNG'
            else:
                logger.warning(f"Unsupported file type: {thumb_extension}")
                return

            temp_thumb = BytesIO()
            img.save(temp_thumb, FTYPE)
            temp_thumb.seek(0)

            self.profile_thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
            temp_thumb.close()

            self.save(update_fields=['profile_thumbnail'])
            logger.info(f"Thumbnail created successfully for user {self.username}")
        except Exception as e:
            logger.error(f"Error creating thumbnail for user {self.username}: {str(e)}")

    # ... (rest of the model remains the same)