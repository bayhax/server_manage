# Generated by Django 3.0.3 on 2020-04-25 05:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server_list', '0003_auto_20200423_1443'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerListUpdate',
            fields=[
                ('server_name', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='服务器名称')),
                ('max_player', models.CharField(max_length=40, verbose_name='在线人数/最大人数')),
                ('cpu', models.CharField(max_length=40, verbose_name='CPU占用率')),
                ('memory', models.CharField(max_length=40, verbose_name='内存占用')),
                ('send_flow', models.CharField(max_length=80, verbose_name='发送流量占用')),
                ('recv_flow', models.CharField(max_length=80, verbose_name='接收流量占用')),
                ('version', models.CharField(max_length=40, verbose_name='版本')),
                ('pattern', models.CharField(max_length=20, verbose_name='模式')),
                ('zone', models.CharField(max_length=20, verbose_name='地区')),
                ('plat', models.CharField(max_length=20, verbose_name='平台')),
                ('run_company', models.CharField(max_length=40, verbose_name='运行商')),
                ('ip', models.CharField(max_length=50, verbose_name='ip地址')),
                ('user', models.CharField(max_length=20, verbose_name='用户')),
                ('port', models.CharField(max_length=20, verbose_name='端口')),
                ('instance_name', models.CharField(max_length=50, null=True, verbose_name='实例名称')),
                ('account', models.CharField(max_length=40, verbose_name='账户')),
                ('time', models.DateTimeField(auto_now=True, verbose_name='日期')),
                ('is_activate', models.IntegerField(default=0, verbose_name='服务器状态')),
                ('server_rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server_list.ServerNameRule', verbose_name='服务器列表_服务器名称规则id')),
            ],
            options={
                'verbose_name': '服务器最新状态表',
                'verbose_name_plural': '服务器最新状态表',
                'db_table': 'zero_server_list_update',
            },
        ),
    ]
