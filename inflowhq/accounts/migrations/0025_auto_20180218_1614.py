# Generated by Django 2.0.2 on 2018-02-18 21:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0024_userassociatedtypes_userfreelancetype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userassociatedtypes',
            name='UserAccount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='IdAccount'),
        ),
        migrations.AlterField(
            model_name='userassociatedtypes',
            name='UserFreelanceType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='accounts.UserType'),
        ),
        migrations.AlterField(
            model_name='usergoogleinformation',
            name='UserAccount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, unique=True, verbose_name='IdAccount'),
        ),
        migrations.AlterField(
            model_name='userlinkedininformation',
            name='UserAccount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, unique=True, verbose_name='IdAccount'),
        ),
        migrations.AlterField(
            model_name='userpaymenthistory',
            name='UserAccount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='IdAccount'),
        ),
    ]
