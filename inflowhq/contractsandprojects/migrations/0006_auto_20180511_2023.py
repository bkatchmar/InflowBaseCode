# Generated by Django 2.0.2 on 2018-05-12 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contractsandprojects', '0005_auto_20180505_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='KillFee',
            field=models.DecimalField(decimal_places=5, default=0.0, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='NumberOfAllowedRevisions',
            field=models.PositiveSmallIntegerField(default=3),
        ),
    ]
