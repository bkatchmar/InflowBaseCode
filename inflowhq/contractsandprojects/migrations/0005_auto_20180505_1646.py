# Generated by Django 2.0.2 on 2018-05-05 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contractsandprojects', '0004_auto_20180429_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='milestone',
            name='Delivered',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='milestone',
            name='ScheduledDeliveryDate',
            field=models.DateField(null=True),
        ),
    ]
