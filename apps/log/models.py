# from django.conf import settings
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from db.base_model import BaseModel
from django.db import models


class BreakLogSearch(BaseModel):
    """崩溃日志查询模型类"""
    objects = models.Manager()
    server_name = models.CharField(max_length=40, verbose_name='服务器名称')
    max_player = models.CharField(max_length=40, verbose_name='在线人数/最大人数')
    cpu = models.CharField(max_length=40, verbose_name='CPU占用率')
    memory = models.CharField(max_length=40, verbose_name='内存占用')
    send_flow = models.CharField(max_length=80, verbose_name='发送流量占用')
    recv_flow = models.CharField(max_length=80, verbose_name='接收流量占用')
    version = models.CharField(max_length=40, verbose_name='版本')
    zone = models.CharField(max_length=20, verbose_name='地区')
    plat = models.CharField(max_length=20, verbose_name='平台')
    run_company = models.CharField(max_length=40, verbose_name='运行商')
    ip = models.CharField(max_length=50, verbose_name='ip地址')
    user = models.CharField(max_length=20, verbose_name='用户')
    time = models.DateTimeField(auto_now=True, verbose_name='日期')

    class Meta:
        db_table = 'zero_break_log_search'
        verbose_name = '崩溃日志查询'
        verbose_name_plural = verbose_name
