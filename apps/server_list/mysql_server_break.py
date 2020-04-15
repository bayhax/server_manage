#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
import pymysql


def search(server_name, start, end, time_start, time_end):
    # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    db = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = """select time,max_player,cpu,memory,send_flow,recv_flow from zero_break_log_search where server_name='%s' and 
    (time >= '%s' or '%s'='') and (time <='%s' or '%s'='') and (hour(time)>='%s' or '%s'='') 
    and (hour(time)<'%s' or '%s'='');;""" % (server_name, start, start, end, end, time_start, time_start, time_end, time_end)

    cursor.execute(sql)
    # 使用 fetchone() 方法获取全部数据.
    count_data = cursor.fetchall()

    # 关闭数据库连接
    cursor.close()
    db.close()

    return count_data


if __name__ == '__main__':
    search(server_name='', start='', end='', time_start='', time_end='')
