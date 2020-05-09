#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import paramiko

from config.models import Version
from server_list.models import ServerPid, ServerListUpdate, ServerNameRule


def open_server(ip, user, server_name, pid):
    # 创建SSHClient 实例对象
    ssh = paramiko.SSHClient()
    # 调用方法，表示没有存储远程机器的公钥，允许访问
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 查询出filename_uuid
    server_name_temp = ServerPid.objects.get(pid=pid, flag=0).server_name
    uuid = Version.objects.get(server_name=server_name_temp).filename_uuid
    # 连接远程机器，地址，端口，用户名密码
    ssh.connect(
        hostname=ip,
        username=user
    )

    # 删除zero_server_pid表中数据
    ServerPid.objects.filter(server_name=server_name).delete()
    # pid_exist = []
    # 获取已经存在的服务器进程号
    pid_cmd = "top -b -n 1 | grep SandBox | awk '{print $1}'"
    stdin, stdout, stderr = ssh.exec_command(pid_cmd)
    pid_exist = stdout.read().decode('utf-8').rstrip().split('\n')
    # print(pid_exist)
    # 开启服务器之前，要指定两个可用的端口号用来聊天和游戏服务器使用
    # 获取已经存在的端口号,tcp连接
    # exist_port_cmd = "netstat -tnpl | awk 'NR > 2 {print $4}' | awk -F: '{print $NF}'"
    # stdin, stdout, stderr = ssh.exec_command(exist_port_cmd)
    # exist_port_res = stdout.read().decode('utf-8').strip()
    # 已经存在了的端口号
    # exist_port = exist_port_res.split('\n')
    # while True:
    # 随机生成两个个端口号1024，65535之间，游戏服务器端口，游戏聊天窗口
    #    game_port = random.randint(1025, 65534)
    #    chat_port = game_port + 1
    # 判断该端口号是否已经被占用，有则重新生成,没有则使用这个端口
    #    if game_port not in exist_port and chat_port not in exist_port:
    #        break
    # 开启这两个端口，不是永久开启
    # open_game_port = "firewall-cmd --zone=public --add-port=%s/tcp" % game_port
    # ssh.exec_command(open_game_port)
    # open_chat_port = "firewall-cmd --zone=public --add-port=%s/tcp" % chat_port
    # ssh.exec_command(open_chat_port)
    # 改变配置文件中的端口值
    # config_file = '/home/server/%s/SandBox_Data/StreamingAssets/Server/Config.txt' % uuid
    # replace_game_str = '"port" = "%s"' % game_port
    # replace_chat_str = '"chat_port" = "%s"' % chat_port
    # with open(config_file, 'r') as f:
    #    res = f.readlines()
    # res[1] = replace_game_str
    # res[2] = replace_chat_str
    # with open(config_file, 'w') as f:
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
    # 对应的rule_id
    rule_id = ServerNameRule.objects.get(server_name=server_name).id
    server_pid = ServerPid(server_name=server_name, pid=new_pid[0], ip=ip, user=user, flag=1, server_rule_id=rule_id)
    server_pid.save(force_insert=True)

    # 将zero_server_list_update表中的is_activate状态改为1
    ServerListUpdate.objects.filter(server_name=server_name).update(is_activate=1)
    # 关闭ssh连接
    ssh.close()


if __name__ == "__main__":
    open_server(ip='', user='', server_name='', pid='')
