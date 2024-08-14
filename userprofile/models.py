import os
import logging
from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    profile_thumbnail = models.ImageField(upload_to='profile_thumbnails/', null=True, blank=True)
    
    def has_profile_image(self):
        return bool(self.profile_image and self.profile_image.name)

    def has_profile_thumbnail(self):
        return bool(self.profile_thumbnail and self.profile_thumbnail.name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_image:
            self.create_thumbnail()

    def create_thumbnail(self):
        if not self.profile_image:
            return

        logger.info(f"Creating thumbnail for user {self.username}")
        try:
            img = Image.open(self.profile_image.path)
            img.thumbnail((32, 32))
            thumb_name, thumb_extension = os.path.splitext(self.profile_image.name)
            thumb_extension = thumb_extension.lower()
            thumb_filename = f"{thumb_name}_thumb{thumb_extension}"

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

    # Add related_name arguments to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    def __str__(self):
        return self.username