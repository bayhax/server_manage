#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import paramiko
import datetime

from config.models import Version
from server_list.models import ServerPid, ServerListUpdate


def kill(ip, user, filename_uuid, pid, server_name):
    # 创建SSHClient 实例对象
    ssh = paramiko.SSHClient()
    # 调用方法，表示没有存储远程机器的公钥，允许访问
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接远程机器，地址，端口，用户名密码
    ssh.connect(
        hostname=ip,
        username=user
    )

    # 置flag.txt标记为0
    change_flag_cmd = "echo '0' > /home/server/%s/flag.txt" % filename_uuid
    # print(change_flag_cmd)
    stdin, stdout, stderr = ssh.exec_command(change_flag_cmd)
    temp = stdout.read().decode('utf-8')
    start_time = datetime.datetime.now()
    while True:
        # 查询出端口号
        search_port = r"cat /home/server/%s/SandBox_Data/StreamingAssets/Server/Config.txt | awk 'NR==2 {print $3}' | awk -F\" '{print $2}'" % filename_uuid
        stdin, stdout, stderr = ssh.exec_command(search_port)
        port = stdout.read().decode('utf-8').strip()
        # 查询出进程号
        search_pid = "lsof -i:%s | grep SandBox | awk '{print $2}'" % port
        stdin, stdout, stderr = ssh.exec_command(search_pid)
        kill_pid = stdout.read().decode('utf-8').strip()
        # 如果pid已经不存在，说明进程已经退出或被杀掉
        if kill_pid == "":
            break

        # 正常退出服务器
        quit_cmd = "cd /home/server/%s;echo 'quit' > in.pipe" % filename_uuid
        # print(quit_cmd)
        stdin, stdout, stderr = ssh.exec_command(quit_cmd)
        temp = stdout.read().decode('utf-8')

        # 杀掉tail的pipe
        if kill_pid != "":
            kill_pipe_cmd = "kill %d" % (int(kill_pid) - 1)
            stdin, stdout, stderr = ssh.exec_command(kill_pipe_cmd)
            temp = stdout.read().decode('utf-8')
        # 如果发送退出命令长时间没有响应，则程序已经崩溃，kill掉
        end_time = datetime.datetime.now()
        if (end_time - start_time).seconds > 5:
            # 杀死进程
            kill_pid_cmd = "kill %s" % kill_pid
            stdin, stdout, stderr = ssh.exec_command(kill_pid_cmd)
            temp = stdout.read().decode('utf-8')
            # 确保服务器完全关闭
            # time.sleep(1)
            break

    # 删除之前的端口
    old_port_cmd = "cat /home/server/%s/SandBox_Data/StreamingAssets/Server/Config.txt | awk 'NR==2 {print $3}'" % filename_uuid
    stdint, stdout, stderr = ssh.exec_command(old_port_cmd)
    old_port = int(stdout.read().decode('utf-8').strip().replace('"', ''))
    old_chat_port = old_port + 1
    # print("old:%d, %d" % (old_port, old_chat_port))
    # 移除端口
    remove_game_port = "firewall-cmd --zone=public --permanent --remove-port=%s/udp" % old_port
    stdin, stdout, stderr = ssh.exec_command(remove_game_port)
    temp = stdout.read().decode('utf-8')
    remove_chat_port = "firewall-cmd --zone=public --permanent --remove-port=%s/udp" % old_chat_port
    stdin, stdout, stderr = ssh.exec_command(remove_chat_port)
    temp = stdout.read().decode('utf-8')

    # 将nohup文件拷贝一份放到/home下，在开启更新的服务器前，拷贝过去
    copy_cmd = "cp /home/server/%s/nohup.out /home" % filename_uuid
    stdin, stdout, stderr = ssh.exec_command(copy_cmd)
    temp = stdout.read().decode('utf-8')

    # 删除原来的服务器文件
    rm_cmd = "rm -rf /home/server/%s" % filename_uuid
    stdin, stdout, stderr = ssh.exec_command(rm_cmd)
    temp = stdout.read().decode('utf-8')

    # 删除数据库中存放的该服务器的相关信息，zero_server_pid,zero_version,zero_server_list_update
    ServerPid.objects.filter(server_name=server_name).delete()
    Version.objects.filter(server_name=server_name).delete()
    ServerListUpdate.objects.filter(server_name=server_name).delete()

    # 关闭ssh连接
    ssh.close()


if __name__ == "__main__":
    # ip/user/filename_uuid/pid
    kill('49.232.21.147', 'root', filename_uuid='', pid='', server_name='删档测试二服')
