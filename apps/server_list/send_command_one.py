#!/root/.virtualenvs/server/bin/python3
import datetime

import paramiko
# import pymysql

from config.models import Version
from server_list.models import ServerPid, CommandLog, ServerNameRule


def send(server_name, ip, user, command):
    # 创建SSHClient 实例对象
    ssh = paramiko.SSHClient()
    # 调用方法，表示没有存储远程机器的公钥，允许访问
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接远程机器，地址，端口，用户名密码
    ssh.connect(
        hostname=ip,
        username=user
    )
    # 连接数据库
    # conn = pymysql.connect('localhost', 'root', 'P@ssw0rd1', 'zero_server')
    # cursor = conn.cursor()
    # sql = "select filename_uuid from zero_version where server_name='%s';" % server_name
    # cursor.execute(sql)
    # uuid = cursor.fetchone()[0]
    uuid = Version.objects.get(server_name=server_name).filename_uuid

    if command == 'quit':
        # 将zero_server_pid的flag变成0，将服务器文件夹下的flag.txt文件中的值置为0
        # sql_cmd = "update zero_server_pid set flag=0 where server_name='%s';" % server_name
        # cursor.execute(sql_cmd)
        # conn.commit()
        ServerPid.objects.filter(server_name=server_name).update(flag=0)
        # 将文件标志置为0
        ssh_cmd = "echo '0' > /home/server/%s/flag.txt" % uuid
        stdin, stdout, stderr = ssh.exec_command(ssh_cmd)
        temp = stdout.read().decode('utf-8')

    cmd = "cd /home/server/%s;echo '%s' > in.pipe" % (uuid, command)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    temp = stdout.read().decode('utf-8')

    rule_id = ServerNameRule.objects.get(server_name=server_name).id
    command_log = CommandLog(server_name=server_name, send_command=command, server_rule_id=rule_id,
                             time=datetime.datetime.now())
    command_log.save(force_insert=True)
    # insert_sql = """insert into zero_command_log(server_name,send_command,time)
    #         values('%s','%s',CURTIME());""" % (server_name, command)
    #
    # cursor.execute(insert_sql)
    #
    # # 只有提交后数据库才会有数据
    # conn.commit()

    # 关闭ssh连接，关闭数据库
    ssh.close()
    # cursor.close()
    # conn.close()


if __name__ == "__main__":
    send('删档测试二服', '192.144.238.49', 'root', 'count')
