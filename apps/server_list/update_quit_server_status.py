#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
import pymysql


def update(server_name):
    try:
        # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
        db = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()

        sql = """update zero_server_list_update set is_activate=0 where server_name='%s';""" % server_name

        cursor.execute(sql)
        db.commit()
        # 关闭数据库连接
        db.close()

    except Exception as e:
        raise e


if __name__ == '__main__':
    update(server_name="删档测试一服")
