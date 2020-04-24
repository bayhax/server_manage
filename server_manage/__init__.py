from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app
import pymysql
pymysql.install_as_MySQLdb()

# 确保django项目启动会一直使用celery
__all__ = ('celery_app',)
