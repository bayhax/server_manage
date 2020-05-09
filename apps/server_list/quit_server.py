#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################

import paramiko
# import pymysql
from django_redis import get_redis_connection

from config.models import Version
from server_list.models import ServerNameRule, ServerPid


def quit_server(ip, user, filename_uuid):
    try:
        redis_conn = get_redis_connection('default')
        # 创建SSHClient 实例对象
        ssh = paramiko.SSHClient()
        # 调用方法，表示没有存储远程机器的公钥，允许访问
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接远程机器，地址，端口，用户名密码
        ssh.connect(
            hostname=ip,
            username=user
        )
        
        # 获取服务器名
        server_name = Version.objects.get(filename_uuid=filename_uuid).server_name
        
        # 杀掉tail pipe管道进程
        # 查询出端口号
        search_port = r"""cat /home/server/%s/SandBox_Data/StreamingAssets/Server/Config.txt | awk 'NR==2 {print $3}' 
        | awk -F\" '{print $2}'""" % filename_uuid
        stdin, stdout, stderr = ssh.exec_command(search_port)
        port = stdout.read().decode('utf-8').strip()
        # 查询出进程号
        search_pid = "lsof -i:%s | grep SandBox | awk '{print $2}'" % port
        stdin, stdout, stderr = ssh.exec_command(search_pid)
        kill_pid = stdout.read().decode('utf-8').strip()
        
        # 连接远程服务器发送命令退出，关闭服务器
        quit_cmd = "cd /home/server/%s;echo 'quit' > in.pipe" % filename_uuid
        # print(quit_cmd)
        temp = ssh.exec_command(quit_cmd)
       
        # 杀掉tail的pipe
        if kill_pid != "":
            kill_pipe_cmd = "kill %d" % (int(kill_pid) - 1)
            temp = ssh.exec_command(kill_pipe_cmd)
       
        # 将标志文件flag.txt改为0
        flag_cmd = "echo '0' > /home/server/%s/flag.txt" % filename_uuid
        temp = ssh.exec_command(flag_cmd)
        
        # 更新zero_server_pid表flag状态为0,表示正常关闭服务器，不是异常死亡，定时检测程序不会重新开启此服务器
        ServerPid.objects.filter(server_name=server_name).update(flag=0)
        server_id = ServerNameRule.objects.get(server_name=server_name).id
        data = redis_conn.hget('server:%d' % server_id, 'max_player')
        redis_conn.hmset('server:%d' % server_id,
                         {'max_player': '0/' + (data.decode('utf-8')).split('/')[-1],
                          'cpu': 0.0, 'memory': 0.0, 'send_flow': 0, 'recv_flow': 0, 'is_activate': 0})

    except Exception as e:
        raise e

    # 关闭ssh连接
    ssh.close()


if __name__ == "__main__":
    quit_server(ip='192.144.238.49', user='root', filename_uuid='03c7617a69ae11ea874f000c2964f883')
