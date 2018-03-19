# Generated by Django 2.0.2 on 2018-03-19 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inflowco', '0003_country'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailSignup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Address', models.EmailField(max_length=254)),
                ('Group', models.CharField(choices=[('g', 'General'), ('b', 'Blog')], default='g', max_length=1)),
            ],
            options={
                'db_table': 'EmailSignups',
            },
        ),
    ]
