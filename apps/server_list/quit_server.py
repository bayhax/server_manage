#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################

import paramiko
import pymysql


def quit_server(ip, user, filename_uuid):
    try:
        # 创建SSHClient 实例对象
        ssh = paramiko.SSHClient()
        # 调用方法，表示没有存储远程机器的公钥，允许访问
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接远程机器，地址，端口，用户名密码
        ssh.connect(
            hostname=ip,
            username=user
        )
        # 建立数据库连接
        conn = pymysql.connect('localhost', 'root', 'P@ssw0rd1', 'zero_server')
        cursor = conn.cursor()
        # 查询服务器名
        sql = """select server_name from zero_version where filename_uuid ='%s';""" % filename_uuid
        cursor.execute(sql)
        # 获取服务器名
        server_name = cursor.fetchone()[0]
        # 连接远程服务器发送命令退出，关闭服务器
        quit_cmd = "cd /home/server/%s;echo 'quit' > in.pipe" % filename_uuid
        print(quit_cmd)
        stdin, stdout, stderr = ssh.exec_command(quit_cmd)
        temp = stdout.read().decode('utf-8')
        # 将标志文件flag.txt改为0
        flag_cmd = "echo '0' > /home/server/%s/flag.txt" % filename_uuid
        stdin, stdout, stderr = ssh.exec_command(flag_cmd)
        temp = stdout.read().decode('utf-8')
        # 更新zero_server_pid表flag状态为0,表示正常关闭服务器，不是异常死亡，定时检测程序不会重新开启此服务器
        sql_update = "update zero_server_pid set flag=0 where server_name='%s'" % server_name
        cursor.execute(sql_update)
        conn.commit()

    except Exception as e:
        raise e

    # 关闭数据库和ssh连接
    ssh.close()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    quit_server(ip='192.144.238.49', user='root', filename_uuid='03c7617a69ae11ea874f000c2964f883')
