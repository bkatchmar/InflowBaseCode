# Generated by Django 2.0.2 on 2018-06-12 02:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contractsandprojects', '0009_auto_20180609_0901'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='FreelancerPortfolioPiece',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='recipient',
            name='ZipCode',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
