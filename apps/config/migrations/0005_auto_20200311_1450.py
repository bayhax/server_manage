# Generated by Django 3.0.3 on 2020-03-11 06:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0004_version_pattern'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pattern',
            old_name='pattern_name',
            new_name='pattern',
        ),
    ]
