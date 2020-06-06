from django.db import models

from db.base_model import BaseModel


class ServerNameRule(BaseModel):
    """服务器名称规则表"""
    objects = models.Manager()
    server_name = models.CharField(max_length=40, verbose_name='服务器名称', unique=True)
    zone = models.CharField(max_length=20, verbose_name='地区')
    num = models.IntegerField(default=0, verbose_name='序号')

    class Meta:
        db_table = 'zero_server_name_rule'
        verbose_name = '服务器名称规则表'
        verbose_name_plural = verbose_name


class ServerList(BaseModel):
    """服务器列表模型类"""
    server_name = models.CharField(max_length=40, verbose_name='服务器名称')
    max_player = models.CharField(max_length=40, verbose_name='在线人数/最大人数')
    cpu = models.FloatField(default=0.00, verbose_name='CPU占用率')
    memory = models.FloatField(default=0.00, verbose_name='内存占用')
    send_flow = models.FloatField(default=0.00, verbose_name='发送流量占用',)
    recv_flow = models.FloatField(default=0.00, verbose_name='接收流量占用',)
    version = models.CharField(max_length=40, verbose_name='版本')
    pattern = models.CharField(max_length=20, verbose_name='模式')
    zone = models.CharField(max_length=20, verbose_name='地区')
    plat = models.CharField(max_length=20, verbose_name='平台')
    run_company = models.CharField(max_length=40, verbose_name='运行商')
    ip = models.CharField(max_length=50, verbose_name='ip地址')
    user = models.CharField(max_length=20, verbose_name='用户')
    port = models.CharField(max_length=20, verbose_name='端口')
    instance_id = models.CharField(max_length=50, verbose_name='实例id')
    account = models.CharField(max_length=40, verbose_name='账户')
    time = models.DateTimeField(verbose_name='日期')
    is_activate = models.IntegerField(default=0, verbose_name='服务器状态')
    server_rule = models.ForeignKey(ServerNameRule, on_delete=models.CASCADE, verbose_name='服务器列表_服务器名称规则id')

    class Meta:
        db_table = 'zero_server_list'
        verbose_name = '服务器列表'
        verbose_name_plural = verbose_name


class ServerListUpdate(BaseModel):
    """服务器最新状况表"""
    objects = models.Manager()
    server_name = models.CharField(max_length=40, verbose_name='服务器名称', primary_key=True)
    max_player = models.CharField(max_length=40, verbose_name='在线人数/最大人数')
    cpu = models.FloatField(default=0.00, verbose_name='CPU占用率')
    memory = models.FloatField(default=0.00, verbose_name='内存占用')
    send_flow = models.FloatField(default=0.00, verbose_name='发送流量占用', )
    recv_flow = models.FloatField(default=0.00, verbose_name='接收流量占用', )
    version = models.CharField(max_length=40, verbose_name='版本')
    pattern = models.CharField(max_length=20, verbose_name='模式')
    zone = models.CharField(max_length=20, verbose_name='地区')
    plat = models.CharField(max_length=20, verbose_name='平台')
    run_company = models.CharField(max_length=40, verbose_name='运行商')
    ip = models.CharField(max_length=50, verbose_name='ip地址')
    user = models.CharField(max_length=20, verbose_name='用户')
    port = models.CharField(max_length=20, verbose_name='端口')
    instance_id = models.CharField(max_length=50, verbose_name='实例名称', null=True)
    account = models.CharField(max_length=40, verbose_name='账户')
    time = models.DateTimeField(auto_now=True, verbose_name='日期')
    is_activate = models.IntegerField(default=0, verbose_name='服务器状态')
    server_rule = models.ForeignKey(ServerNameRule, on_delete=models.CASCADE, verbose_name='服务器列表_服务器名称规则id')

    class Meta:
        db_table = 'zero_server_list_update'
        verbose_name = '服务器最新状态表'
        verbose_name_plural = verbose_name


class ServerPid(BaseModel):
    """服务器进程的pid"""
    objects = models.Manager()
    server_name = models.CharField(max_length=40, verbose_name='服务器名称')
    pid = models.CharField(max_length=10, verbose_name='服务器进程号')  # 数字
    ip = models.CharField(max_length=50, verbose_name='ip地址')
    user = models.CharField(max_length=20, verbose_name='用户')
    flag = models.IntegerField(default=1, verbose_name='异常标志')
    server_rule = models.ForeignKey(ServerNameRule, on_delete=models.CASCADE, verbose_name='服务器进程_服务器名称规则id')

    class Meta:
        db_table = 'zero_server_pid'
        verbose_name = '服务器进程pid表'
        verbose_name_plural = verbose_name


class InsType(BaseModel):
    """实例类型所属ip,所属账户"""
    objects = models.Manager()
    ins_type = models.CharField(max_length=40, verbose_name='实例类型')
    ip = models.CharField(max_length=50, verbose_name='ip地址', primary_key=True)
    account_name = models.CharField(max_length=40, verbose_name='账户名称')

    class Meta:
        db_table = 'zero_ins_type'
        verbose_name = '实例类型表'
        verbose_name_plural = verbose_name


class CommandLog(BaseModel):
    """命令日志"""
    objects = models.Manager()
    server_name = models.CharField(max_length=40, verbose_name="服务器名称")
    send_command = models.CharField(max_length=40, verbose_name="命令内容")
    time = models.DateTimeField(auto_now=True, verbose_name='时间')
    server_rule = models.ForeignKey(ServerNameRule, on_delete=models.CASCADE, verbose_name='命令日志_服务器名称规则id')

    class Meta:
        db_table = 'zero_command_log'
        verbose_name = '命令日志表'
        verbose_name_plural = verbose_name
