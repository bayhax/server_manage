# Generated by Django 3.0.3 on 2020-03-11 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cloud_user', '0006_auto_20200310_1435'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account_zone',
            old_name='available_zone',
            new_name='region',
        ),
    ]
