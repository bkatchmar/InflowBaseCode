# Generated by Django 2.0.2 on 2018-06-12 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contractsandprojects', '0010_auto_20180611_2237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipient',
            name='ZipCode',
        ),
        migrations.AddField(
            model_name='recipientaddress',
            name='ZipCode',
            field=models.CharField(max_length=20, null=True),
        ),
    ]