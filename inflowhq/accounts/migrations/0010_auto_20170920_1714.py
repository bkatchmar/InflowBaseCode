# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-20 21:14
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20170920_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersettings',
            name='Joined',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 20, 21, 14, 24, 780134, tzinfo=utc), verbose_name='Joined'),
        ),
    ]
