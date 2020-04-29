# absolute_import 不会与库冲突，python
from __future__ import absolute_import, unicode_literals
import os
from datetime import timedelta
from celery import Celery, platforms
# 定时任务模块
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_manage.settings')

# redis作队列中间件
# app = Celery('server_manage', backend='redis', broker='redis://localhost')
# rabbitmq作消息队列
# app = Celery('server_manage', broker='amqp://guest:guest@localhost')
app = Celery('server_manage')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# 允许root用户运行celery
platforms.C_FORCE_ROOT = True

# 防止内存泄漏
CELERYD_MAX_TASKS_PER_CHILD = 10


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))  # dumps its own request information


# 定时任务配置
CELERYBETA_SCHEDULE={
    'server_status': {
        'task': 'server_list.tasks.server_status',
        'schedule': crontab(minute='*/5'),
    },
    'monitor_process': {
        'task': 'server_list.tasks.monitor_process',
        'schedule': crontab(minute=1),
    },
    'insert_ins_type': {
        'task': 'cloud_user.tasks.insert_ins_type',
        'schedule': crontab(hour=2),
    },
    'insert_account_zone': {
        'task': 'cloud_user.tasks.insert_account_zone',
        'schedule': crontab(hour=2),
    }
}
