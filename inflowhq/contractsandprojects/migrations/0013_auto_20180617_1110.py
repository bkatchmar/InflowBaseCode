# Generated by Django 2.0.2 on 2018-06-17 15:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contractsandprojects', '0012_contractlatereviewcharge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contractlatereviewcharge',
            old_name='HourlyRate',
            new_name='Charge',
        ),
    ]
