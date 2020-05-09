# from db.base_model import BaseModel
from django.db import models

from db.base_model import BaseModel


class Version(BaseModel):
    """文件名对应的版本号"""
    objects = models.Manager()
    filename_uuid = models.CharField(max_length=32, verbose_name='文件名_uuid')
    # filename = models.CharField(max_length=40, verbose_name='上传文件名')
    version = models.CharField(max_length=40, verbose_name='版本号')
    server_name = models.CharField(max_length=40, verbose_name='服务器名称', unique=True)
    pattern = models.CharField(max_length=40, verbose_name='模式')
    zone = models.CharField(max_length=20, verbose_name='地区')
    run_company = models.CharField(max_length=40, verbose_name='运营商')

    class Meta:
        db_table = 'zero_version'
        verbose_name = '文件名版本表'
        verbose_name_plural = verbose_name


class AddVersion(BaseModel):
    """可以新增开设服务器的版本号"""
    objects = models.Manager()
    # filename = models.CharField(max_length=40, verbose_name='上传文件名')
    version = models.CharField(max_length=40, verbose_name='版本号', unique=True)
    plat = models.CharField(max_length=20, verbose_name='平台')

    class Meta:
        db_table = 'zero_add_version'
        verbose_name = '可新增版本表'
        verbose_name_plural = verbose_name


class Pattern(BaseModel):
    """模式配置表模型类"""
    objects = models.Manager()
    ins_type = models.CharField(max_length=40, verbose_name='实例类型')
    pay_type = models.CharField(max_length=20, verbose_name='付费类型')
    pattern = models.CharField(max_length=40, verbose_name='模式名称', unique=True)
    player_num = models.IntegerField(default=1000, verbose_name='单台实例分配在线人数')
    cpu_num = models.IntegerField(default=2, verbose_name='单台实例分配CPU')
    memory_num = models.IntegerField(default=2, verbose_name='单台实例分配内存')
    disk_num = models.IntegerField(default=20, verbose_name='单台实例分配硬盘')
    flow_num = models.IntegerField(default=2, verbose_name='单台实例分配流量')

    class Meta:
        db_table = 'zero_pattern'
        verbose_name = '模式配置表'
        verbose_name_plural = verbose_name


class RunCompany(BaseModel):
    """运营商表模型类"""
    objects = models.Manager()
    run_company_name = models.CharField(max_length=40, verbose_name='运营商名称', unique=True)

    class Meta:
        db_table = 'zero_run_company'
        verbose_name = '运营商配置表'
        verbose_name_plural = verbose_name


class Plat(BaseModel):
    """平台表模型类"""
    objects = models.Manager()
    plat = models.CharField(max_length=40, verbose_name='平台', unique=True)

    class Meta:
        db_table = 'zero_plat'
        verbose_name = '平台配置表'
        verbose_name_plural = verbose_name
