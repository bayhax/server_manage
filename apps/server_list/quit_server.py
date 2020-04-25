#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################

import paramiko
import pymysql
from django_redis import get_redis_connection

from server_list.models import ServerNameRule


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
        # print(quit_cmd)
        temp = ssh.exec_command(quit_cmd)
        # 将标志文件flag.txt改为0
        flag_cmd = "echo '0' > /home/server/%s/flag.txt" % filename_uuid
        temp = ssh.exec_command(flag_cmd)

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
        # 杀掉tail的pipe
        if kill_pid != "":
            kill_pipe_cmd = "kill %d" % (int(kill_pid) - 1)
            temp = ssh.exec_command(kill_pipe_cmd)

        # 更新zero_server_pid表flag状态为0,表示正常关闭服务器，不是异常死亡，定时检测程序不会重新开启此服务器
        sql_update = "update zero_server_pid set flag=0 where server_name='%s'" % server_name
        cursor.execute(sql_update)
        server_id = ServerNameRule.objects.get(server_name=server_name).id
        data = redis_conn.hgetall('server:%d' % server_id)
        data = [x.decode('utf-8') for x in data]
        redis_conn.hmset('server:%d' % server_id,
                         {'max_player': '0/' + data[1].split('/')[-1],
                          'cpu': '0.00%/0.00%-0.00/' + data[2].split('/')[2] + '/' + data[2].split('/')[3],
                          'memory': '0.00%/0.00%-0.00G/' + data[3].split('/')[2] + '/' + data[3].split('/')[3],
                          'send_flow': '0.00%/0.00%-0B/' + data[4].split('/')[2] + '/' + data[4].split('/')[3],
                          'recv_flow': '0.00%/0.00%-0B/' + data[5].split('/')[2] + '/' + data[5].split('/')[3],
                          'is_activate': 0})
        # 更新zero_server_list_update状态相关值为0，（redis缓存相关字段状态设置为0。）
        conn.commit()

    except Exception as e:
        raise e

    # 关闭数据库和ssh连接
    ssh.close()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    quit_server(ip='192.144.238.49', user='root', filename_uuid='03c7617a69ae11ea874f000c2964f883')
