# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-12 02:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_usersettings_stripeapicustomerkey'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='StripeConnectAccountKey',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
