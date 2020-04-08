#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import random

import paramiko
import pymysql


def open_server(ip, user, server_name, pid):
    # 创建SSHClient 实例对象
    ssh = paramiko.SSHClient()
    # 调用方法，表示没有存储远程机器的公钥，允许访问
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 数据库连接
    conn = pymysql.connect('localhost', 'root', 'P@ssw0rd1', 'zero_server')
    # 创建游标对象
    cursor = conn.cursor()
    # 根据pid查询出filename_uuid
    sql = """select filename_uuid from zero_version where server_name=(select server_name from zero_server_pid 
            where flag=0 and pid=%s)""" % pid
    cursor.execute(sql)
    uuid = cursor.fetchone()[0]
    # 连接远程机器，地址，端口，用户名密码
    ssh.connect(
        hostname=ip,
        username=user
    )

    # 删除zero_server_pid表中数据
    sql_delete = "delete from zero_server_pid where server_name='%s';" % server_name
    cursor.execute(sql_delete)
    conn.commit()

    # pid_exist = []
    # 获取已经存在的服务器进程号
    pid_cmd = "top -b -n 1 | grep SandBox | awk '{print $1}'"
    stdin, stdout, stderr = ssh.exec_command(pid_cmd)
    pid_exist = stdout.read().decode('utf-8').rstrip().split('\n')
    # print(pid_exist)
    # 开启服务器之前，要指定两个可用的端口号用来聊天和游戏服务器使用
    # 获取已经存在的端口号,tcp连接
    #exist_port_cmd = "netstat -tnpl | awk 'NR > 2 {print $4}' | awk -F: '{print $NF}'"
    #stdin, stdout, stderr = ssh.exec_command(exist_port_cmd)
    #exist_port_res = stdout.read().decode('utf-8').strip()
    # 已经存在了的端口号
    #exist_port = exist_port_res.split('\n')
    #while True:
        # 随机生成两个个端口号1024，65535之间，游戏服务器端口，游戏聊天窗口
    #    game_port = random.randint(1025, 65534)
    #    chat_port = game_port + 1
        # 判断该端口号是否已经被占用，有则重新生成,没有则使用这个端口
    #    if game_port not in exist_port and chat_port not in exist_port:
    #        break
    # 开启这两个端口，不是永久开启
    #open_game_port = "firewall-cmd --zone=public --add-port=%s/tcp" % game_port
    #ssh.exec_command(open_game_port)
    #open_chat_port = "firewall-cmd --zone=public --add-port=%s/tcp" % chat_port
    #ssh.exec_command(open_chat_port)
    # 改变配置文件中的端口值
    #config_file = '/home/server/%s/SandBox_Data/StreamingAssets/Server/Config.txt' % uuid
    #replace_game_str = '"port" = "%s"' % game_port
    #replace_chat_str = '"chat_port" = "%s"' % chat_port
    #with open(config_file, 'r') as f:
    #    res = f.readlines()
    #res[1] = replace_game_str
    #res[2] = replace_chat_str
    #with open(config_file, 'w') as f:
    #    f.writelines(res)
    # 开启服务器
    start_cmd = "cd /home/server/%s; sh start.sh >> /home/server/%s/nohup.out" % (uuid, uuid)
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    temp = stdout.read().decode('utf-8')
    # 将标志flag.txt置为1
    flag_cmd = "echo '1' > /home/server/%s/flag.txt" % uuid
    stdin, stdout, stderr = ssh.exec_command(flag_cmd)
    temp = stdout.read().decode('utf-8')
    new_pid_cmd = "top -b -n 1 | grep SandBox | awk '{print $1}'"
    stdin, stdout, stderr = ssh.exec_command(new_pid_cmd)
    # 全部服务器进程号，获取新开的服务器进程号
    cur_pid_all = stdout.read().decode('utf-8').rstrip().split('\n')

    # 服务器新的进程号
    new_pid = [x for x in cur_pid_all if x not in pid_exist]
    sql = """insert into zero_server_pid(server_name,pid,ip,user,flag)
        values('%s','%s','%s','%s',1)""" % (server_name, new_pid[0], ip, user)

    cursor.execute(sql)
    conn.commit()
    # 将zero_server_list_update表中的is_activate状态改为1
    sql_start = "update zero_server_list_update set is_activate=1 where server_name='%s';" % server_name
    cursor.execute(sql_start)
    conn.commit()

    # 关闭数据库连接
    ssh.close()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    open_server(ip='', user='', server_name='', pid='')
