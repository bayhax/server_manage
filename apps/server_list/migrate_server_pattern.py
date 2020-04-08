#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
import pymysql


def migrate(server_name, pattern):
    # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    db = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    sql = """update zero_server_list set pattern='%s' where server_name='%s' and time >= date_add(now(), 
            interval - 5 minute);""" % (pattern, server_name)
    # 执行语句
    cursor.execute(sql)

    db.commit()
    # 关闭数据库连接
    cursor.close()
    db.close()


if __name__ == '__main__':
    migrate(server_name='删档测试二服', pattern='normal')
