# Generated by Django 5.0.7 on 2024-09-23 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0006_alter_people_people_pipeline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='people',
            name='people_pipeline',
            field=models.CharField(blank=True, choices=[('PROMOTION', 'PROMOTION'), ('INFORMATION', 'INFORMATION'), ('INVITATION,', 'INVITATION,'), ('CONFIRMATION', 'CONFIRMATION'), ('AUTOMATION', 'AUTOMATION')], max_length=100, null=True),
        ),
    ]
