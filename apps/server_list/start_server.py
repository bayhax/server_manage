#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import os
import time

import paramiko
# import pymysql
import random

from config.models import Version
from server_list.models import ServerPid


def start(flag, ori_ip, ori_user, dest_ip, dest_user, name, version, pattern, zone, run_company, uid, server_name):
    # 数据库连接
    # conn = pymysql.connect('localhost', 'root', 'P@ssw0rd1', 'zero_server')
    # # 创建游标对象
    # cursor = conn.cursor()
    # 创建SSHClient 实例对象
    ssh = paramiko.SSHClient()
    # 调用方法，表示没有存储远程机器的公钥，允许访问
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 如果是在原实例上迁移，只需更改下该服务器的模式配置数据库
        if flag == 0:
            # sql = """update zero_version set pattern='%s' where server_name='%s';""" % (pattern, server_name)
            # cursor.execute(sql)
            Version.objects.filter(server_name=server_name).update(pattern=pattern)
        # 要迁移到其他实例上
        else:
            # 连接原实例，删除该服务器文件夹
            ssh.connect(
                hostname=ori_ip,
                username=ori_user
            )
            # 根据服务器名称查询出filename_uuid
            # select_sql = """select filename_uuid from zero_version where server_name='%s';""" % server_name
            # cursor.execute(select_sql)
            # filename_uuid = cursor.fetchone()[0]
            filename_uuid = Version.objects.get(server_name=server_name).filename_uuid
            # 关闭服务器，置flag.txt文件标志为0
            # 连接远程服务器，退出选中的服务器的进程并删除服务器文件,将flag.txt标记置为0，防止传输文件时间过长，服务器重启
            quit_cmd = "cd /home/server/%s;echo 'quit' > in.pipe" % filename_uuid
            # print(quit_cmd)
            stdin, stdout, stderr = ssh.exec_command(quit_cmd)
            temp = stdout.read().decode('utf-8')
            # 使程序完全关闭
            time.sleep(1)
            # 置flag.txt标记为0
            change_flag_cmd = "echo '0' > /home/server/%s/flag.txt" % filename_uuid
            print(change_flag_cmd)
            stdin, stdout, stderr = ssh.exec_command(change_flag_cmd)
            temp = stdout.read().decode('utf-8')
            # 删除之前的端口
            old_port_cmd = "cat /home/server/%s/SandBox_Data/StreamingAssets/Server/Config.txt | awk 'NR==2 {print $3}'" % filename_uuid
            stdint, stdout, stderr = ssh.exec_command(old_port_cmd)
            old_port = int(stdout.read().decode('utf-8').strip().replace('"', ''))
            old_chat_port = old_port + 1
            print("old:%d, %d" % (old_port, old_chat_port))
            # 移除端口
            remove_game_port = "firewall-cmd --zone=public --permanent --remove-port=%s/udp" % old_port
            stdin, stdout, stderr = ssh.exec_command(remove_game_port)
            temp = stdout.read().decode('utf-8')
            remove_chat_port = "firewall-cmd --zone=public --permanent --remove-port=%s/udp" % old_chat_port
            stdin, stdout, stderr = ssh.exec_command(remove_chat_port)
            temp = stdout.read().decode('utf-8')

            # 将nohup文件拷贝一份放到/home下，在开启更新的服务器前，拷贝过去
            copy_cmd = "scp /home/server/%s /home/migrate" % filename_uuid
            os.system(copy_cmd)
            # 拷贝存档文件
            copy_save_cmd = "scp -r /root/.config/unity3d/zerO3D/Zero-based\ World/%s /home/migrate" % (server_name)
            os.system(copy_save_cmd)
            # 删除原来的服务器文件
            rm_cmd = "rm -rf /home/server/%s" % filename_uuid
            stdin, stdout, stderr = ssh.exec_command(rm_cmd)
            temp = stdout.read().decode('utf-8')
            rm_save_cmd = "rm -rf /root/.config/unity3d/zerO3D/Zero-based\ World/%s" % server_name
            stdin, stdout, stderr = ssh.exec_command(rm_save_cmd)
            temp = stdout.read().decode('utf-8')
            # 断开ssh连接
            ssh.close()
            # 连接目的端ssh
            ssh.connect(
                hostname=dest_ip,
                username=dest_user
            )
            # 将服务器文件还有存档文件拷贝置相应目录下。。
            copy_file_to_dest = "scp -r /home/migrate/%s %s@%s:/home/server" % (filename_uuid, dest_user, dest_ip)
            os.system(copy_file_to_dest)
            copy_save_to_dest = "scp -r /home/migrate/%s %s@%s:/root/.config/unity3d/zerO3D/Zero-based\ World" % \
                                (filename_uuid, dest_user, dest_ip)
            os.system(copy_save_to_dest)
            # 开启端口，替换端口
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
            start_cmd = "cd /home/server/%s;chmod +x SandBox.x86_64; sh start.sh >> /home/server/%s/nohup.out" % (uid, uid)
            stdin, stdout, stderr = ssh.exec_command(start_cmd)
            temp = stdout.read().decode('utf-8')
            #     stdin, stdout, stderr = ssh.exec_command(open_chat_port)

            # 更新zero_version表
            # sql = """update zero_version set pattern='%s' where server_name='%s';""" % (pattern, server_name)
            # cursor.execute(sql)
            Version.objects.filter(server_name=server_name).update(pattern=pattern)
            # 更新zero_server_pid表
            # 获取已经存在的服务器进程号
            pid_cmd = "top -b -n 1 | grep SandBox | awk '{print $1}'"
            stdin, stdout, stderr = ssh.exec_command(pid_cmd)
            pid_exist = stdout.read().decode('utf-8').rstrip().split('\n')
            # print(pid_exist)

            new_pid_cmd = "top -b -n 1 | grep SandBox | awk '{print $1}'"
            stdin, stdout, stderr = ssh.exec_command(new_pid_cmd)
            # 全部服务器进程号，获取新开的服务器进程号
            cur_pid_all = stdout.read().decode('utf-8').rstrip().split('\n')
            # print(cur_pid_all)

            # 新开服务器进程号
            new_pid = [x for x in cur_pid_all if x not in pid_exist]
            # update_sql = "update zero_server_pid set pid='%s',ip='%s',user='%s',flag=1 where server_name='%s';" % \
            #              (new_pid[0], dest_ip, dest_user, server_name)
            # cursor.execute(update_sql)
            # conn.commit()
            ServerPid.objects.filter(server_name=server_name).update(pid=new_pid[0], ip=dest_ip, user=dest_user, flag=1)

    except Exception as e:
        raise e

    # 关闭ssh远程连接
    ssh.close()
    # cursor.close()
    # conn.close()


if __name__ == "__main__":
    # ip/user/实例名称/账户名称
    start(flag=0, ori_ip='49.232.21.147', ori_user='root', dest_ip='', dest_user='', name='LinuxServer',
          version='server1.0.3', pattern='test', zone='华北地区(北京)', run_company='taptap', uid='', server_name='')
