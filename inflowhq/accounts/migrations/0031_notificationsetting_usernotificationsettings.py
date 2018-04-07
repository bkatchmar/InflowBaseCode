# Generated by Django 2.0.2 on 2018-04-06 02:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0030_auto_20180405_2228'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SettingName', models.TextField()),
            ],
            options={
                'db_table': 'NotificationSetting',
            },
        ),
        migrations.CreateModel(
            name='UserNotificationSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Selected', models.BooleanField()),
                ('Setting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.NotificationSetting')),
                ('UserAccount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='IdAccount')),
            ],
            options={
                'db_table': 'UserNotificationSettings',
            },
        ),
    ]