# Generated by Django 5.0.7 on 2024-09-04 16:52

import contacts.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('church_name', models.CharField(blank=True, max_length=100, null=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, null=True, upload_to=contacts.models.get_image_path)),
                ('preferred_contact_method', models.CharField(choices=[('email', 'Email'), ('phone', 'Phone'), ('text', 'Text'), ('Facebook Messanger', 'Facebook Messanger'), ('whatsapp', 'Whatsapp'), ('groupme', 'Groupme'), ('signal', 'Signal'), ('other', 'Other')], max_length=100)),
                ('phone', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('street_address', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, choices=[('al', 'AL'), ('ak', 'AK'), ('az', 'AZ'), ('ar', 'AR'), ('ca', 'CA'), ('co', 'CO'), ('ct', 'CT'), ('de', 'DE'), ('fl', 'FL'), ('ga', 'GA'), ('hi', 'HI'), ('id', 'ID'), ('il', 'IL'), ('in', 'IN'), ('ia', 'IA'), ('ks', 'KS'), ('ky', 'KY'), ('la', 'LA'), ('me', 'ME'), ('md', 'MD'), ('ma', 'MA'), ('mi', 'MI'), ('mn', 'MN'), ('ms', 'MS'), ('mo', 'MO'), ('mt', 'MT'), ('ne', 'NE'), ('nv', 'NV'), ('nh', 'NH'), ('nj', 'NJ'), ('nm', 'NM'), ('ny', 'NY'), ('nc', 'NC'), ('nd', 'ND'), ('oh', 'OH'), ('ok', 'OK'), ('or', 'OR'), ('pa', 'PA'), ('ri', 'RI'), ('sc', 'SC'), ('sd', 'SD'), ('tn', 'TN'), ('tx', 'TX'), ('ut', 'UT'), ('vt', 'VT'), ('va', 'VA'), ('wa', 'WA'), ('wv', 'WV'), ('wi', 'WI'), ('wy', 'WY'), ('dc', 'DC')], max_length=2, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=10, null=True)),
                ('initial_notes', models.TextField(blank=True, null=True)),
                ('date_created', models.DateField(auto_now_add=True, null=True)),
                ('date_modified', models.DateField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Church',
            fields=[
                ('contact_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='contacts.contact')),
                ('virtuous', models.BooleanField(default=False)),
                ('senior_pastor_first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('senior_pastor_last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('senior_pastor_phone', models.CharField(blank=True, max_length=50, null=True)),
                ('senior_pastor_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('missions_pastor_first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('missions_pastor_last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('mission_pastor_phone', models.CharField(blank=True, max_length=50, null=True)),
                ('mission_pastor_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('primary_contact_first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('primary_contact_last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('primary_contact_phone', models.CharField(blank=True, max_length=200, null=True)),
                ('primary_contact_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('denomination', models.CharField(blank=True, max_length=100, null=True)),
                ('congregation_size', models.IntegerField(blank=True, null=True)),
                ('church_pipeline', models.CharField(choices=[('PROMOTION','PROMOTION'), ('INFORMATION','INFORMATION'), ('INVITATION', 'INVITATION'), ('CONFIRMATION', 'CONFIRMATION'), ('EN42', 'EN42'), ('AUTOMATION', 'AUTOMATION')], default='PROMOTION', max_length=100)),
                ('priority', models.CharField(choices=[('URGENT', 'URGENT'), ('HIGH', 'HIGH'), ('MEDIUM', 'MEDIUM'), ('LOW', 'LOW')], default='MEDIUM', max_length=10)),
                ('assigned_to', models.CharField(choices=[('BILL JONES', 'BILL JONES'), ('JASON MODOMO', 'JASON MODOMO'), ('KEN KATAYAMA', 'KEN KATAYAMA'), ('MATTHEW RULE', 'MATTHEW RULE'), ('CHIP ATKINSON', 'CHIP ATKINSON'), ('RACHEL LIVELY', 'RACHEL LIVELY'), ('JIM BURCHEL', 'JIM BURCHEL'), ('JILL WALKER', 'JILL WALKER'), ('KARINA RAMPIN', 'KARINA RAMPIN'), ('UNASSIGNED', 'UNASSIGNED')], default='UNASSIGNED', max_length=100)),
                ('source', models.CharField(choices=[('WEBFORM', 'WEBFORM'), ('INCOMING CALL', 'INCOMING CALL'), ('EMAIL', 'EMAIL'), ('SOCIAL MEDIA', 'SOCIAL MEDIA'), ('COLD CALL', 'COLD CALL'), ('PERSPECTIVES', 'PERSPECTIVES'), ('REFERAL', 'REFERAL'), ('OTHER', 'OTHER'), ('UNKNOWN', 'UNKNOWN')], default='UNKNOWN', max_length=100)),
                ('referred_by', models.CharField(blank=True, max_length=100, null=True)),
                ('info_given', models.TextField(blank=True, null=True)),
                ('reason_closed', models.TextField(blank=True, null=True)),
                ('year_founded', models.IntegerField(blank=True, null=True)),
                ('date_closed', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Church',
                'verbose_name_plural': 'Churches',
            },
            bases=('contacts.contact',),
        ),
        migrations.CreateModel(
            name='People',
            fields=[
                ('contact_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='contacts.contact')),
                ('spouse_first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('spouse_last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('virtuous', models.BooleanField(default=False)),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('home_country', models.CharField(blank=True, max_length=100, null=True)),
                ('marital_status', models.CharField(blank=True, choices=[('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced'), ('widowed', 'Widowed'), ('separated', 'Separated'), ('unknown', 'Unknown'), ('engaged', 'Engaged')], max_length=100, null=True)),
                ('people_pipeline', models.CharField(blank=True, choices=[('uncontacted', 'Uncontacted'), ('contacted', 'Contacted'), ('mission-vision', 'Mission Vision'), ('conversations', 'Conversations'), ('potential-recruit', 'Potential Recruit'), ('automated', 'Automated')], max_length=100, null=True)),
                ('priority', models.CharField(blank=True, choices=[('urgent', 'Urgent'), ('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], max_length=100, null=True)),
                ('assigned_to', models.CharField(blank=True, choices=[('BILL JONES', 'BILL JONES'), ('JASON MODOMO', 'JASON MODOMO'), ('KEN KATAYAMA', 'KEN KATAYAMA'), ('MATTHEW RULE', 'MATTHEW RULE'), ('CHIP ATKINSON', 'CHIP ATKINSON'), ('RACHEL LIVELY', 'RACHEL LIVELY'), ('JIM BURCHEL', 'JIM BURCHEL'), ('JILL WALKER', 'JILL WALKER'), ('KARINA RAMPIN', 'KARINA RAMPIN'), ('UNASSIGNED', 'UNASSIGNED')], max_length=100, null=True)),
                ('source', models.CharField(blank=True, choices=[('WEBFORM', 'WEBFORM'), ('INCOMING CALL', 'INCOMING CALL'), ('EMAIL', 'EMAIL'), ('INSTAGRAM', 'INSTAGRAM'), ('FACEBOOK', 'FACEBOOK'), ('X - TWITTER', 'X- TWITTER'), ('LINKEDIN', 'LINKEDIN'), ('COLD CALL', 'COLD CALL'), ('PERSPECTIVES', 'PERSPECTIVES'), ('REFERAL', 'REFERAL'), ('CIU', 'CIU'), ('CHURCH', 'CHURCH'), ('OTHER', 'OTHER')], max_length=100, null=True)),
                ('referred_by', models.CharField(blank=True, max_length=100, null=True)),
                ('info_given', models.TextField(blank=True, null=True)),
                ('desired_service', models.TextField(blank=True, null=True)),
                ('reason_closed', models.TextField(blank=True, null=True)),
                ('date_closed', models.DateField(blank=True, null=True)),
                ('color', models.CharField(blank=True, max_length=20, null=True)),
                ('affiliated_church', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contacts.church', verbose_name='Affiliated Church')),
            ],
            options={
                'verbose_name': 'Person',
                'verbose_name_plural': 'People',
                'ordering': ['last_name', 'first_name'],
            },
            bases=('contacts.contact',),
        ),
    ]
