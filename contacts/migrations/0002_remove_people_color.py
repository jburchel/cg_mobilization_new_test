# Generated by Django 5.0.7 on 2024-09-04 18:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='people',
            name='color',
        ),
    ]
