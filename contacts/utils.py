from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
import os

def create_thumbnail(image_field, size=(100, 100)):
    """
    Creates a thumbnail of the given image field.
    Returns the thumbnail as a ContentFile.
    """
    img = Image.open(image_field)
    img.thumbnail(size)
    thumb_io = BytesIO()
    img.save(thumb_io, img.format, quality=85)
    thumbnail = ContentFile(thumb_io.getvalue())
    return thumbnail

def get_thumbnail_path(instance, filename):
    """
    Returns the path for storing thumbnails.
    """
    # Get the original image path
    original_path = instance.image.path
    # Get the directory of the original image
    directory = os.path.dirname(original_path)
    # Get the filename without extension
    name = os.path.splitext(os.path.basename(original_path))[0]
    # Return the new path
    return os.path.join(directory, 'thumbnails', f"{name}_thumb.jpg")