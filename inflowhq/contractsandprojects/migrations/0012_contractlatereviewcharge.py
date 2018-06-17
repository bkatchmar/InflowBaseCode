# Generated by Django 2.0.2 on 2018-06-17 14:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contractsandprojects', '0011_auto_20180611_2304'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractLateReviewCharge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DaysLateTolerance', models.IntegerField()),
                ('HourlyRate', models.DecimalField(decimal_places=3, default=0.0, max_digits=10)),
                ('TimeWindowToleranceType', models.CharField(choices=[('d', 'Per Day'), ('w', 'Per Week')], default='d', max_length=1)),
                ('ContractForCharge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contractsandprojects.Contract', unique=True)),
            ],
            options={
                'db_table': 'ContractLateReviewCharge',
            },
        ),
    ]
