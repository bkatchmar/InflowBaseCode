# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-06 00:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contractsandprojects', '0005_auto_20171005_2028'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationship',
            name='ContractUser',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
