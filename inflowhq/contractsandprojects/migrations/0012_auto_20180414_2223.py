# Generated by Django 2.0.2 on 2018-04-15 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contractsandprojects', '0011_milestone_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='EndDate',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='contract',
            name='StartDate',
            field=models.DateField(),
        ),
    ]