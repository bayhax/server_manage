# Generated by Django 3.0.3 on 2020-04-30 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_list', '0006_auto_20200427_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverlist',
            name='time',
            field=models.DateTimeField(verbose_name='日期'),
        ),
    ]
