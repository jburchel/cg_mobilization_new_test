from django import template
import os

register = template.Library()

@register.filter
def filename(value):
    return os.path.basename(value)

@register.filter
def remove_extension(value):
    return os.path.splitext(value)[0]