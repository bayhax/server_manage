# Generated by Django 3.0.3 on 2020-04-30 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0003_auto_20200423_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='breaklogsearch',
            name='time',
            field=models.DateTimeField(verbose_name='日期'),
        ),
    ]
