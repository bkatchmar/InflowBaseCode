# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-06 22:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inflowco', '0002_auto_20170925_0647'),
        ('contractsandprojects', '0006_relationship_contractuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PaymentType', models.CharField(choices=[('o', 'ONE TIME'), ('w', 'WEEKLY'), ('b', 'BI WEEKLY'), ('m', 'MONTHLY')], default='o', max_length=1)),
                ('TotalPaymentAmount', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('ContractCurrency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inflowco.Currency')),
            ],
            options={
                'db_table': 'ContractPaymentPlan',
            },
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=200)),
                ('Address', models.CharField(max_length=200)),
                ('State', models.CharField(max_length=100)),
                ('Email', models.EmailField(max_length=254)),
                ('City', models.CharField(max_length=200)),
                ('Country', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'ContractRecipient',
            },
        ),
        migrations.RemoveField(
            model_name='contract',
            name='ContractCurrency',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='PaymentType',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='RecipientAddress',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='RecipientCity',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='RecipientCountry',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='RecipientEmail',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='RecipientName',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='RecipientState',
        ),
        migrations.AlterField(
            model_name='relationship',
            name='RelationshipType',
            field=models.CharField(choices=[('f', 'FREELANCER'), ('c', 'CLIENT')], default='f', max_length=1),
        ),
        migrations.AddField(
            model_name='recipient',
            name='ContractForRecipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contractsandprojects.Contract', unique=True),
        ),
        migrations.AddField(
            model_name='paymentplan',
            name='ContractForPaymentPlan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contractsandprojects.Contract', unique=True),
        ),
    ]
