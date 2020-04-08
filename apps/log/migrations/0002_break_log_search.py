# Generated by Django 3.0.3 on 2020-02-29 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('log', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='break_log_search',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server_name', models.CharField(max_length=40, verbose_name='服务器名称')),
                ('version', models.CharField(max_length=10, verbose_name='版本')),
                ('zone', models.CharField(max_length=20, verbose_name='地区')),
                ('plat', models.CharField(max_length=20, verbose_name='平台')),
                ('run_company', models.CharField(max_length=40, verbose_name='运行商')),
                ('ip', models.CharField(max_length=20, verbose_name='ip地址')),
                ('user', models.CharField(max_length=20, verbose_name='用户')),
                ('time', models.DateTimeField(auto_now=True, verbose_name='日期')),
            ],
            options={
                'verbose_name': '崩溃日志查询',
                'verbose_name_plural': '崩溃日志查询',
                'db_table': 'zero_break_log_search',
            },
        ),
    ]
