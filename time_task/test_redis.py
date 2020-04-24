#！/root/.virtualenvs/server/bin/python3
# -*- coding:utf-8 -*-
# @Time: 4/23/20 11:51 AM
# @Author:bayhax
# @Filename: test_redis.py
import redis
r = redis.Redis(host="127.0.0.1", port=6379)
print(r.hkeys("*"))
r.hmset('server:1', {'name': 'wag', 'age': 16})
# r.expire('server:1', 25)

print(r.ttl('server:1'))