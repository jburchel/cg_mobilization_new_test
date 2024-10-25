import os
import logging
from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.html import linebreaks
from django.core.files.storage import default_storage
from django.core.files import File

logger = logging.getLogger(__name__)

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    profile_thumbnail = models.ImageField(upload_to='profile_thumbnails/', null=True, blank=True)
    email_signature = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not is_new:
            old_instance = CustomUser.objects.get(pk=self.pk)
            if self.profile_image and self.profile_image != old_instance.profile_image:
                logger.info(f"Profile image changed for user {self.username}. Creating thumbnail.")
                super().save(*args, **kwargs)  # Save first to ensure the image is stored
                self.create_thumbnail()
                super().save(update_fields=['profile_thumbnail'])  # Save again to update the thumbnail field
            else:
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
            if self.profile_image:
                self.create_thumbnail()
                super().save(update_fields=['profile_thumbnail'])

        if self.email_signature:
            self.email_signature = linebreaks(self.email_signature)

    def create_thumbnail(self):
        if not self.profile_image:
            logger.info(f"No profile image for user {self.username}")
            return

        logger.info(f"Creating thumbnail for user {self.username}")
        try:
            with default_storage.open(self.profile_image.name, 'rb') as f:
                img = Image.open(f)
                img.thumbnail((30, 30))
                thumb_io = BytesIO()
                
                img_format = img.format or 'JPEG'
                img.save(thumb_io, format=img_format)
                
                file_extension = 'jpg' if img_format == 'JPEG' else img_format.lower()
                thumb_filename = f'{self.username}_thumb.{file_extension}'
                
                # Save the thumbnail with just the filename
                self.profile_thumbnail.save(thumb_filename, ContentFile(thumb_io.getvalue()), save=False)
                logger.info(f"Thumbnail created successfully for user {self.username}. Path: {self.profile_thumbnail.name}")
        except Exception as e:
            logger.error(f"Error creating thumbnail for user {self.username}: {str(e)}")
