# Generated by Django 5.0.7 on 2024-09-03 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0004_alter_customuser_groups_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='google_refresh_token',
            field=models.CharField(blank=True, max_length=260, null=True),
        ),
    ]