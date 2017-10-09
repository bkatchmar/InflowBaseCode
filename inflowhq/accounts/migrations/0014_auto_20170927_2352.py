# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-28 03:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20170925_0647'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpaymenthistory',
            name='PaymentAmount',
            field=models.DecimalField(decimal_places=2, default=16.0, max_digits=6, verbose_name='PaymentAmount'),
        ),
        migrations.AlterField(
            model_name='userpaymenthistory',
            name='DateCharged',
            field=models.DateField(verbose_name='DateCharged'),
        ),
        migrations.AlterField(
            model_name='userpaymenthistory',
            name='NextBillingDate',
            field=models.DateField(verbose_name='NextBillingDate'),
        ),
    ]
