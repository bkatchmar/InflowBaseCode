# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-20 21:04
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20170920_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersettings',
            name='BaseCurrency',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inflowco.Currency', verbose_name='IdBaseCurrency'),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='Joined',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 20, 21, 4, 8, 808305, tzinfo=utc), verbose_name='Joined'),
        ),
    ]
