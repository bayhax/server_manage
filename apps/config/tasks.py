#！/root/.virtualenvs/server/bin/python3
# -*- coding:utf-8 -*-
# @Time: 4/22/20 3:13 PM
# @Author:bayhax
# @Filename: tasks.py
from __future__ import absolute_import
from celery import shared_task


@shared_task
def test():
    pass
