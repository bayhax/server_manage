#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
import pymysql


def update(server_name, version):
    # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    db = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    sql = """update zero_server_list set version='%s' where server_name='%s' and time >= date_add(now(), interval - 5 minute);""" % (
    version, server_name)
    # 服务其台数      
    cursor.execute(sql)

    db.commit()
    # 关闭数据库连接
    cursor.close()
    db.close()


if __name__ == '__main__':
    update(server_name='删档测试二服', version='1.3')
