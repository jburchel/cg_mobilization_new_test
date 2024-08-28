import os
import logging
from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.conf import settings
logger = logging.getLogger(__name__)

fs = FileSystemStorage(location=settings.MEDIA_ROOT)

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    profile_thumbnail = models.ImageField(upload_to='profile_thumbnails/', null=True, blank=True)
    email_signature = models.TextField(blank=True, null=True)
    signature_logo = models.ImageField(upload_to='signature_logos/', null=True, blank=True)

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_image = None if is_new else CustomUser.objects.get(pk=self.pk).profile_image
        
        super().save(*args, **kwargs)
        
        if is_new or (self.profile_image and self.profile_image != old_image):
            self.create_thumbnail()

    def create_thumbnail(self):
        if not self.profile_image:
            logger.info(f"No profile image for user {self.username}")
            return

        logger.info(f"Creating thumbnail for user {self.username}")
        try:
            img_path = self.profile_image.path
            logger.info(f"Profile image path: {img_path}")
            
            img = Image.open(img_path)
            img.thumbnail((100, 100))  # Adjust size as needed
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG')
            
            thumb_filename = f'{self.username}_thumb.jpg'
            thumb_path = os.path.join('profile_thumbnails', thumb_filename)
            
            self.profile_thumbnail.save(
                thumb_path,
                ContentFile(thumb_io.getvalue()),
                save=False
            )
            self.save(update_fields=['profile_thumbnail'])
            logger.info(f"Thumbnail created successfully for user {self.username}")
        except Exception as e:
            logger.error(f"Error creating thumbnail for user {self.username}: {str(e)}")
            
    def create_signature_logo_thumbnail(self):
        if not self.signature_logo:
            return

        try:
            img = Image.open(self.signature_logo.path)
            img.thumbnail((200, 100))  # Adjust size as needed for email signatures
            thumb_io = BytesIO()
            img.save(thumb_io, format='PNG')
            
            thumb_filename = f'{self.username}_signature_logo_thumb.png'
            thumb_path = os.path.join('signature_logos', thumb_filename)

            self.signature_logo.save(
                thumb_path,
                ContentFile(thumb_io.getvalue()),
                save=False
            )
            self.save(update_fields=['signature_logo'])
        except Exception as e:
            logger.error(f"Error creating signature logo thumbnail for user {self.username}: {str(e)}")