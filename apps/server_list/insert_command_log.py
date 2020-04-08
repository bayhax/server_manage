#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import pymysql


def insert_command(server_name, command):
    # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    conn = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()
    sql = """insert into zero_command_log(server_name,send_command,time) values('%s','%s',CURTIME());""" % (
        server_name, command)

    cursor.execute(sql)

    # 只有提交后数据库才会有数据
    conn.commit()

    cursor.close()
    # 关闭数据库连接
    conn.close()


if __name__ == "__main__":
    # server_name/command
    insert_command('删档测试二服', 'count')
