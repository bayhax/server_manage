#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import random

import paramiko
import pymysql
import os
import uuid


def update_server(ip, user, name, version, pattern, zone, run_company, server_name):
    # 创建SSHClient 实例对象
    ssh = paramiko.SSHClient()
    # 调用方法，表示没有存储远程机器的公钥，允许访问
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接远程机器，地址，端口，用户名密码
    ssh.connect(
            hostname=ip,
            username=user
    )

    # 数据库连接
    conn = pymysql.connect('localhost', 'root', 'P@ssw0rd1', 'zero_server')
    # 创建游标对象
    cursor = conn.cursor()

    # 在拷贝到服务器之前生成唯一uuid,在拷贝到服务器之后替换文件名
    while True:
        # 获取uuid
        uid = uuid.uuid1()
        uid = str(uid).replace('-', '')

        # sql语句
        sql = """select count(*) from zero_version where filename_uuid = '%s';""" % uid
        # 执行语句，获取uuid文件名是否存在,存在则循环重新获取uuid，不存在则入库
        cursor.execute(sql)
        data = cursor.fetchone()

        if data[0] == 0:
            # 将启动服务器命令脚本拷贝至文件内
            cmd_start = "cp /home/server/start.sh /home/server/%s" % name
            os.system(cmd_start)
            # 将服务器初始标志flag.txt拷贝之文件内
            cmd_flag = "cp /home/server/flag.txt /home/server/%s" % name
            os.system(cmd_flag)

            # 修改服务器名称
            config_file = '/home/server/%s/SandBox_Data/StreamingAssets/Server/Config.txt' % name
            replace_str = '"ServerName" = "%s"' % server_name
            # server_name = zone + '_' + str(num)
            with open(config_file, 'r') as f:
                res = f.readlines()
            res[0] = replace_str + '\n'
            with open(config_file, 'w') as f:
                f.writelines(res)
            # sql_insert = "insert into zero_server_name_rule(server_name, zone, num) values('%s','%s',%d);" \
            #              % ((zone + '_' + str(num)), zone, num)
            # cursor.execute(sql_insert)
            # conn.commit()
            # 结束
            break

    # 拷贝到相应的实例服务器文件夹下，利用uid替换服务器的文件名称
    copy_cmd = "scp -r /home/server/%s root@%s:/home/server/%s && scp /home/server/has_complete.txt root@%s:/home/server/" % (name, ip, uid, ip)
    os.system(copy_cmd)
    # 判断验证文件是否已经复制过去
    while True:
        judge_cmd = "[ -f /home/server/has_complete.txt ] && echo '1' || echo '0'"
        stdin, stdout, stderr = ssh.exec_command(judge_cmd)
        if stdout.read().decode('utf-8').strip() == "1":
            # 已经有了验证文件,说明服务器文件已经拷贝完成,删除验证文件
            delete_cmd = "rm -f /home/server/has_complete.txt"
            stdin, stdout, stderr = ssh.exec_command(delete_cmd)
            temp = stdout.read().decode('utf-8')
            break

    # pid_exist = []
    # 获取已经存在的服务器进程号
    pid_cmd = "top -b -n 1 | grep SandBox | awk '{print $1}'"
    stdin, stdout, stderr = ssh.exec_command(pid_cmd)
    pid_exist = stdout.read().decode('utf-8').rstrip().split('\n')
    # print(pid_exist)

    # 开启服务器之前，要指定两个可用的端口号用来聊天和游戏服务器使用
    # 获取已经存在的端口号,udp连接
    exist_port_cmd = "netstat -unpl | awk 'NR > 2 {print $4}' | awk -F: '{print $NF}'"
    stdin, stdout, stderr = ssh.exec_command(exist_port_cmd)
    exist_port_res = stdout.read().decode('utf-8').strip()
    # 已经存在了的端口号
    exist_port = exist_port_res.split('\n')
    while True:
       # 随机生成两个个端口号1024，65535之间，游戏服务器端口，游戏聊天窗口
       game_port = random.randint(1025, 65534)
       chat_port = game_port + 1
        # 判断该端口号是否已经被占用，有则重新生成,没有则使用这个端口
       if game_port not in exist_port and chat_port not in exist_port:
           break
    # 改变配置文件中的端口值
    config_file = '/home/server/%s/SandBox_Data/StreamingAssets/Server/Config.txt' % uid
    replace_game_str = '"Port" = "%s"' % game_port
    # 修改端口名
    change_port = "sed -i '2c %s' %s" % (replace_game_str, config_file)
    # print(change_port)
    stdin, stdout, stderr = ssh.exec_command(change_port)
    temp = stdout.read().decode('utf-8')
    # 开启服务器
    # 判断/home下有没有nohup.out文件，如果有，拷贝过去，删除/home/nohup.out这个时更新服务器，不是新开服
    is_exist = "[ -f /home/nohup.out ] && echo '1' || echo '0'"
    stdin, stdout, stderr = ssh.exec_command(is_exist)
    if stdout.read().decode('utf-8').strip() == "1":
        copy_nohup = "cp /home/nohup.out /home/server/%s/; rm -f /home/nohup.out" % uid
        stdin, stdout, stderr = ssh.exec_command(copy_nohup)
        temp = stdout.read().decode('utf-8')
    start_cmd = "cd /home/server/%s;chmod +x SandBox.x86_64; sh start.sh > /home/server/%s/nohup.out" % (uid, uid)
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    temp = stdout.read().decode('utf-8')

    # 开启这两个端口,永久开启
    open_game_port = "firewall-cmd --zone=public --permanent --add-port=%s/udp" % game_port
    stdin, stdout, stderr = ssh.exec_command(open_game_port)
    temp = stdout.read().decode('utf-8')
    open_chat_port = "firewall-cmd --zone=public --permanent --add-port=%s/udp" % chat_port
    stdin, stdout, stderr = ssh.exec_command(open_chat_port)
    temp = stdout.read().decode('utf-8')

    # 重启防火墙
    restart_firewall = "systemctl restart firewalld"
    stdin, stdout, stderr =ssh.exec_command(restart_firewall)
    temp = stdout.read().decode('utf-8')

    new_pid_cmd = "top -b -n 1 | grep SandBox | awk '{print $1}'"
    stdin, stdout, stderr = ssh.exec_command(new_pid_cmd)
    # 全部服务器进程号，获取新开的服务器进程号
    cur_pid_all = stdout.read().decode('utf-8').rstrip().split('\n')
    # print(cur_pid_all)

    # 新开服务器进程号
    new_pid = [x for x in cur_pid_all if x not in pid_exist]
    # print(new_pid)
    # 存入数据库
    try:
        # 将服务器名称，对应的文件名uuid和模式插入到数据库
        insert_sql = """insert into zero_version(filename_uuid,filename,version,server_name,pattern,zone,run_company)
                                values('%s','%s','%s','%s','%s','%s','%s');""" % \
                     (uid, name, version, server_name, pattern, zone, run_company)
        # print(insert_sql)
        cursor.execute(insert_sql)

        # 将服务器和进程号插入数据库
        sql = """insert into zero_server_pid(server_name,pid,ip,user,flag) values('%s','%s','%s','%s',1);""" % (server_name, new_pid[0],ip,user)
        # sql = """update zero_server_pid set pid='%s' where server_name='%s'""" % (new_pid[0], server_name)
        cursor.execute(sql)
    except Exception as e:
        raise e

    # 数据库提交
    conn.commit()
    # 关闭ssh远程连接
    ssh.close()
    cursor.close()
    conn.close()

    return uid


if __name__ == "__main__":
    # ip/user/实例名称/账户名称
    update_server(ip='49.232.21.147', user='root', name='LinuxServer', version='server1.0.3', pattern='test',
                  zone='华北地区(北京)', run_company='taptap', server_name='')
