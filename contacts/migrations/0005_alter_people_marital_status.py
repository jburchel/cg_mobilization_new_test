# Generated by Django 5.0.7 on 2024-08-22 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0004_alter_church_mission_pastor_phone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='people',
            name='marital_status',
            field=models.CharField(blank=True, choices=[('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced'), ('widowed', 'Widowed'), ('separated', 'Separated'), ('unknown', 'Unknown'), ('engaged', 'Engaged')], max_length=100, null=True),
        ),
    ]
