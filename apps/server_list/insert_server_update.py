#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
# import re
import time
import datetime

import paramiko

from django_redis import get_redis_connection
from config.models import Version, AddVersion
from server_list.models import ServerListUpdate, ServerPid, ServerNameRule


def insert_mysql(ip, user, uid):
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

    cmd = "cd /home/server/%s/SandBox_Data/StreamingAssets/Server;awk '{print $3}' Config.txt" % uid
    # 接受执行结果
    stdin, stdout, stderr = ssh.exec_command(cmd)
    # 对结果进行分组，服务器名称，端口，最大在线人数
    result = stdout.read().decode('utf-8').replace("\r", "").replace('"', '').strip().split('\n')
    # 该台实例下的服务器名称
    server_name = result[0]
    # 该服务器的端口
    server_port = result[1]
    # 该服务器的最大在线人数
    server_max_player = result[2]
    # 发送命令取在线人数
    online_cmd = "echo 'count' > /home/server/%s/in.pipe" % uid
    stdin, stdout, stderr = ssh.exec_command(online_cmd)
    temp = stdout.read().decode('utf-8')
    time.sleep(1)
    get_player_cmd = "cat /home/server/%s/nohup.out | awk 'END {print}'" % uid
    stdin, stdout, stderr = ssh.exec_command(get_player_cmd)
    # 在线人数结果
    online_str = stdout.read().decode('utf-8').strip()
    if online_str == '' or len(online_str) > 4:
        print('没有拿到在线人数，可能时服务器未完全开启。')
        online = 0
    else:
        online = int(online_str)
    # 判断该服务器是否繁忙
    if online / int(result[2]) > (1 / 2):
        busy_server += 1
    else:
        relax_server += 1

    # 取出该服务器的进程号
    pid = ServerPid.objects.get(server_name=server_name).pid

    # cpu占用率
    # 本身占用,str
    cpucmd = "top -b -n 1 | grep -w '%s' | awk '{print $9}'" % pid
    stdin, stdout, stderr = ssh.exec_command(cpucmd)
    cpu = stdout.read().decode('utf-8').strip()

    # 内存占用
    # 当前内存,str
    memcmd = "top -b -n 1 | grep -w '%s' | awk '{print $10}'" % pid
    stdin, stdout, stderr = ssh.exec_command(memcmd)
    memory = stdout.read().decode('utf-8').strip()

    # 流量占用
    # 当前流量占用
    # 发送流量占用,接收结果去除空格
    send_cmd = "cat flow.txt | grep %s | awk 'END {print $2}'" % pid
    stdin, stdout, stderr = ssh.exec_command(send_cmd)
    send_flow = stdout.read().decode('utf-8').strip()
    if send_flow == '':
        send_flow = str(0)
    # 接收流量占用，接收结果去除空格
    recv_cmd = "cat flow.txt | grep %s | awk 'END {pring $3}'" % pid
    stdin, stdout, stderr = ssh.exec_command(recv_cmd)
    recv_flow = stdout.read().decode('utf-8').strip()
    if recv_flow == '':
        recv_flow = str(0)

    # 服务器信息
    server_info = Version.objects.get(filename_uuid=uid)
    # 根据服务器版本查询出平台
    plat = AddVersion.objects.get(version=server_info.version).plat
    rule_id = ServerNameRule.objects.get(server_name=server_name).id
    # 存在则更新,不存在插入
    server_update = ServerListUpdate(server_name=server_name, max_player=str(online) + '/' + server_max_player,
                                     cpu=cpu, memory=memory, send_flow=send_flow, recv_flow=recv_flow,
                                     version=server_info.version, pattern=server_info.pattern, zone=server_info.zone,
                                     plat=plat, run_company=server_info.run_company, ip=ip, user=user, port=server_port,
                                     time=datetime.datetime.now() + datetime.timedelta(hours=8), account='', instance_id='1',
                                     is_activate=1, server_rule_id=rule_id)
    server_update.save()
    redis_conn = get_redis_connection('default')
    redis_conn.hmset('server:%d' % rule_id,
                     {'server_name': server_name, 'max_player': str(online) + '/' + server_max_player,
                      'cpu': cpu, 'memory': memory, 'send_flow': send_flow, 'recv_flow': recv_flow,
                      'version': server_info.version, 'pattern': server_info.pattern,
                      'zone': server_info.zone, 'plat': plat, 'run_company': server_info.run_company, 'ip': ip,
                      'user': user, 'port': server_port, 'is_activate': 1, 'server_rule_id': rule_id})
    # 关闭ssh连接
    ssh.close()


if __name__ == "__main__":
    # ip/user/实例名称/账户名称
    # insert_mysql('192.144.238.49,'root','192.144.238.49_server','沃德天·维森莫')
    insert_mysql('49.232.21.147', 'root', uid='')
