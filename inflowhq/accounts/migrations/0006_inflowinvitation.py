# Generated by Django 2.0.2 on 2018-05-19 02:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0005_remove_usersettings_freelancerinterestedin'),
    ]

    operations = [
        migrations.CreateModel(
            name='InFlowInvitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('GUID', models.CharField(max_length=40)),
                ('Expiry', models.DateField()),
                ('InvitedUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'InFlowInvitation',
            },
        ),
    ]
