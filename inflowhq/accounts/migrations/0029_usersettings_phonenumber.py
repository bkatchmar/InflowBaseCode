# Generated by Django 2.0.2 on 2018-04-03 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0028_auto_20180218_2253'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='PhoneNumber',
            field=models.CharField(max_length=20, null=True),
        ),
    ]