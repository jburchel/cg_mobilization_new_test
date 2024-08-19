from django.db import migrations
from django.contrib.contenttypes.models import ContentType

def handle_null_values(apps, schema_editor):
    ComLog = apps.get_model('com_log', 'ComLog')
    default_content_type = ContentType.objects.get_for_model(ComLog)

    for com_log in ComLog.objects.filter(content_type__isnull=True) | ComLog.objects.filter(object_id__isnull=True):
        if com_log.content_type is None:
            com_log.content_type = default_content_type
        if com_log.object_id is None:
            com_log.object_id = '0'  # Use a placeholder value
        com_log.save()

class Migration(migrations.Migration):

    dependencies = [
        ('com_log', '0002_alter_comlog_content_type_alter_comlog_object_id'),  # replace with the name of your previous migration
    ]

    operations = [
        migrations.RunPython(handle_null_values),
    ]