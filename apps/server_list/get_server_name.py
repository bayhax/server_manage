#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import paramiko


def servername(ip, user):
    server_list = []
    server_name = []  # 服务器名字
    server_port = []  # 服务器端口
    server_max_player = []  # 服务器最大在线人数，列表存起来对应每个服务器
    busy_server = 0
    relax_server = 0
    # 创建SSHClient 实例对象
    ssh = paramiko.SSHClient()
    # 调用方法，表示没有存储远程机器的公钥，允许访问
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接远程机器，地址，端口，用户名密码
    ssh.connect(
        hostname=ip,
        username=user
    )
    # 目录；浏览服务器所在目录
    cmd = 'ls /home'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode('utf-8').split('\n')
    # print(result)
    for name in result:
        if 'LinuxServer' in name:
            # print(name)
            server_list.append(name)
    # print(server_list)
    for server in server_list:
        cmd = "cd /home/%s/SandBox_Data/StreamingAssets/Server;awk '{print $3}' Config.txt" % server
        # 接受执行结果
        stdin, stdout, stderr = ssh.exec_command(cmd)
        # 对结果进行分组，服务器名称，端口，最大在线人数
        result = stdout.read().decode('utf-8').replace("\r", "").replace('"', '').strip().split('\n')
        # 该台实例下的服务器名称列表
        server_name.append(result[0])
        # 该服务器的端口
        server_port.append(result[1])
        # 该服务器的最大在线人数
        server_max_player.append(result[2])
        # 发送命令取在线人数
        online_cmd = "cd /home/%s; echo 'count' > in.pipe; cat nohup.out | awk 'END {print}'" % server
        stdin, stdout, stderr = ssh.exec_command(online_cmd)
        # 在线人数结果
        online = int(stdout.read().decode('utf-8'))
        # 判断该服务器是否繁忙
        if online / int(result[2]) > (1 / 2):
            busy_server += 1
        else:
            relax_server += 1

    ssh.close()
    return server_name, server_max_player, busy_server, relax_server


if __name__ == "__main__":
    servername('49.232.21.147', 'root')
