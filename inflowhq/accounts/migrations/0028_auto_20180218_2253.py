# Generated by Django 2.0.2 on 2018-02-19 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_auto_20180218_2156'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='BusinessName',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='usersettings',
            name='Region',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
