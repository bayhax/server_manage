from db.base_model import BaseModel
from django.db import models


# Create your models here.


class Account(BaseModel):
    """云账户表模型类"""
    objects = models.Manager()
    account_name = models.CharField(max_length=40, verbose_name='账户名称')
    account_id = models.CharField(max_length=50, verbose_name='账户id')
    account_key = models.CharField(max_length=50, verbose_name='账户key')

    class Meta:
        db_table = 'zero_cloud_user'
        verbose_name = '云账户表'
        verbose_name_plural = verbose_name


class AccountZone(BaseModel):
    """账户区域表模型类"""
    objects = models.Manager()
    account_name = models.CharField(max_length=40, verbose_name='账户名称')
    account_id = models.CharField(max_length=50, verbose_name='账户id')
    account_key = models.CharField(max_length=50, verbose_name='账户key')
    region = models.CharField(max_length=1024, verbose_name='可用区', null=True)

    class Meta:
        db_table = 'zero_account_zone'
        verbose_name = '账户可用区表'
        verbose_name_plural = verbose_name


class ZoneCode(BaseModel):
    """可用区域中文对码表"""
    zone = models.CharField(max_length=60, verbose_name='区域中文')
    code = models.CharField(max_length=60, verbose_name='区域代码')

    class Meta:
        db_table = 'zero_zone_code'
        verbose_name = '可用区代码表'
        verbose_name_plural = verbose_name


class ServerAccountZone(BaseModel):
    """可新增服务器地区表"""
    objects = models.Manager()
    account_name = models.CharField(max_length=40, verbose_name='账户名称')
    zone = models.CharField(max_length=60, verbose_name='可新增服务器地区')

    class Meta:
        unique_together = ['account_name', 'zone']
        db_table = 'zero_server_account_zone'
        verbose_name = '可新增服务器地区表'
        verbose_name_plural = verbose_name
