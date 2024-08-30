# Generated by Django 5.0.7 on 2024-08-30 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0004_alter_church_mission_pastor_phone_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='people',
            name='',
            field=models.CharField(blank=True, choices=[('Student PR', 'Student PR'), ('Student', 'Student'), ('Webform', 'Webform'), ('Church PR', 'Church PR'), ('Couple PR', 'Couple PR'), ('Denied', 'Denied'), ('Intern', 'Intern')], max_length=100, null=True),
        ),
        
        migrations.AlterField(
            model_name='church',
            name='church_pipeline',
            field=models.CharField(choices=[('COLD', 'COLD'), ('WARM', 'WARM'), ('CONTACTED', 'CONTACTED'), ('MISSION VISION', 'MISSION VISION'), ('COMMITTED', 'COMMITTED'), ('EN42', 'EN42'), ('AUTOMATED', 'AUTOMATED')], default='UNKNOWN', max_length=100),
        ),
        
        migrations.AlterField(
            model_name='people',
            name='marital_status',
            field=models.CharField(blank=True, choices=[('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced'), ('widowed', 'Widowed'), ('separated', 'Separated'), ('unknown', 'Unknown'), ('engaged', 'Engaged')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='people',
            name='people_pipeline',
            field=models.CharField(blank=True, choices=[('uncontacted', 'Uncontacted'), ('contacted', 'Contacted'), ('mission-vision', 'Mission Vision'), ('conversations', 'Conversations'), ('potential-recruit', 'Potential Recruit'), ('automated', 'Automated')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='people',
            name='source',
            field=models.CharField(blank=True, choices=[('WEBFORM', 'WEBFORM'), ('INCOMING CALL', 'INCOMING CALL'), ('EMAIL', 'EMAIL'), ('INSTAGRAM', 'INSTAGRAM'), ('FACEBOOK', 'FACEBOOK'), ('X - TWITTER', 'X- TWITTER'), ('LINKEDIN', 'LINKEDIN'), ('COLD CALL', 'COLD CALL'), ('PERSPECTIVES', 'PERSPECTIVES'), ('REFERAL', 'REFERAL'), ('CIU', 'CIU'), ('CHURCH', 'CHURCH'), ('OTHER', 'OTHER')], max_length=100, null=True),
        ),
    ]
