#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import paramiko
import pymysql


def insert_mysql(ip,user):
    #创建SSHClient 实例对象
    ssh=paramiko.SSHClient()
    #调用方法，表示没有存储远程机器的公钥，允许访问
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #连接远程机器，地址，端口，用户名密码
    ssh.connect(
            hostname=ip,
            username=user
    )

    # 数据库连接
    conn = pymysql.connect('localhost','root','P@ssw0rd1','zero_server')
    # 创建游标对象
    cursor = conn.cursor()

    #目录；浏览服务器所在目录
    cmd = 'ls /home/server'
    stdin,stdout,stderr = ssh.exec_command(cmd)
    result = stdout.read().decode('utf-8').split('\n')
    pid_exist = []
    #print(result)
    for name in result:
        if 'LinuxServer' in name:
            pid_exist = []
            # 查看该服务器的名称
            cmd = "cd /home/server/%s/SandBox_Data/StreamingAssets/Server;awk 'NR==1 {print $3}' Config.txt" % name
            # 接受执行结果
            stdin, stdout, stderr = ssh.exec_command(cmd)
            # 对结果进行分组，服务器名称，端口，最大在线人数
            server_name = stdout.read().decode('utf-8').replace('"','').strip()
            # 该台实例下的服务器名称列表
            #print(server_name)
            
            # 获取已经存在的服务器进程号
            pid_cmd = "top -b -n 1 | grep SandBox.x8+ | awk '{print $1}'"
            stdin, stdout, stderr = ssh.exec_command(pid_cmd)
            pid_exist = stdout.read().decode('utf-8').rstrip().split('\n')
            #print(pid_exist)

            # 开启服务器
            start_cmd = "sh /home/server/%s/start.sh > /home/server/%s/nohup.out" % (name,name)

            stdin, stdout, stderr = ssh.exec_command(start_cmd)
            temp = stdout.read().decode('utf-8')
            new_pid_cmd = "top -b -n 1 | grep SandBox.x8+ | awk '{print $1}'"
            stdin, stdout, stderr = ssh.exec_command(new_pid_cmd)
            
            # 全部服务器进程号，获取新开的服务器进程号
            cur_pid_all = stdout.read().decode('utf-8').rstrip().split('\n')
            #print(cur_pid_all)
            new_pid = [x for x in cur_pid_all if x not in pid_exist]
            #print(server_name,new_pid)
            
            sql = """insert into zero_server_pid(server_name,pid,ip,user) values('%s','%s','%s','%s')""" % (server_name,new_pid[0],ip,user)
            cursor.execute(sql)
            conn.commit()
    # 关闭ssh远程连接
    ssh.close()

if __name__ == "__main__":
    # ip/user/实例名称/账户名称
    insert_mysql('192.144.238.49','root')

