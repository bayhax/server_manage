#！/root/.virtualenvs/server/bin/python3
# -*- coding:utf-8 -*-
# @Time: 4/22/20 3:16 PM
# @Author:bayhax
# @Filename: tasks.py
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import os
# from server_manage.celery import app


@shared_task()
def test():
    print("hello")
