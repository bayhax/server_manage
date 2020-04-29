#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
# import re
import time
import datetime

import paramiko
# import pymysql


# def data_merge(itself, allocate, instance, signal):
#     # 本身占用/分配占用
#     self_alloc = str(format(float(itself) / float(allocate), '.2f'))
#     # 本身占用/实例最大占用
#     self_ins = str(format(float(itself) / float(instance), '.2f'))
#
#     # 组合数据
#     merge = self_alloc + "%/" + self_ins + "%-" + str(itself) + signal + "/" + str(allocate) + signal + "/" + \
#             str(instance) + signal
#
#     return merge
from config.models import Version, AddVersion
from server_list.models import ServerListUpdate, ServerPid, ServerNameRule


def insert_mysql(ip, user, uid):
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

    # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    # conn = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # # 使用 cursor() 方法创建一个游标对象 cursor
    # cursor = conn.cursor()

    # server_list_update_server_name = []
    # zero_server_list_update表中所有服务器名称
    # sql = """select server_name from zero_server_list_update;"""
    # cursor.execute(sql)
    # data = cursor.fetchall()
    # for d in data:
    #     server_list_update_server_name.append(d[0])
    # server_list_update_server_name = ServerListUpdate.objects.all().values_list('server_name', flat=True)

    cmd = "cd /home/server/%s/SandBox_Data/StreamingAssets/Server;awk '{print $3}' Config.txt" % uid
    # 接受执行结果
    stdin, stdout, stderr = ssh.exec_command(cmd)
    # 对结果进行分组，服务器名称，端口，最大在线人数
    result = stdout.read().decode('utf-8').replace("\r", "").replace('"', '').strip().split('\n')
    # 该台实例下的服务器名称
    server_name.append(result[0])
    # 该服务器的端口
    server_port.append(result[1])
    # 该服务器的最大在线人数
    server_max_player.append(result[2])
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

    # 根据服务器名称在zero_version表中取出模式名称
    # sql_pattern = """select pattern from zero_version where server_name = '%s';""" % result[0]
    # cursor.execute(sql_pattern)
    # pattern = cursor.fetchone()
    # pattern = pattern[0]
    # pattern = Version.objects.get(server_name=result[0]).pattern
    # 在zero_pattern表中取出该模式的分配信息,结果为元组
    # sql_allocate = """select cpu_num,memory_num,flow_num from zero_pattern where pattern='%s';""" % pattern
    # cursor.execute(sql_allocate)
    # allocate = cursor.fetchone()
    # allocate = Pattern.objects.filter(pattern=pattern).values_list('cpu_num', 'memory_num', 'flow_num')
    # 根据ip在zero_ins_type表中取出ins_type，即实例最大
    # sql_instance = "select ins_type from zero_ins_type where ip='%s';" % ip
    # cursor.execute(sql_instance)
    # instance_max = cursor.fetchone()
    # instance_max = InsType.objects.get(ip=ip).ins_type
    # 利用正则表达式将实例最大配置的数字取出来
    # instance_max = re.findall(r"\d+\.?\d*", instance_max)

    # 取出该服务器的进程号
    # sql_pid = """select pid from zero_server_pid where server_name = '%s'""" % result[0]
    # cursor.execute(sql_pid)
    # pid = cursor.fetchone()
    # pid = pid[0]
    pid = ServerPid.objects.get(server_name=result[0]).pid

    # print(pid)
    # cpu占用率
    # 本身占用,str
    cpucmd = "top -b -n 1 | grep -w '%s' | awk '{print $9}'" % pid
    stdin, stdout, stderr = ssh.exec_command(cpucmd)
    cpu = stdout.read().decode('utf-8').strip()
    # print(cpu)
    # 分配占用,int
    # cpu_allocate = allocate[0]

    # 实例最大占用,str
    # cpu_instance = instance_max[0]

    # cpu组合数据 
    # cpu_merge = data_merge(format(float(cpu) * int(cpu_instance) / 100, ".2f"), cpu_allocate, cpu_instance, '')

    # 内存占用
    # 当前内存,str
    memcmd = "top -b -n 1 | grep -w '%s' | awk '{print $10}'" % pid
    stdin, stdout, stderr = ssh.exec_command(memcmd)
    memory = stdout.read().decode('utf-8').strip()

    # 分配内存,int
    # mem_allocate = allocate[1]
    #
    # # 实例最大占用,str
    # mem_instance = instance_max[1]

    # 内存组合数据
    # mem_merge = data_merge(format(float(mem) * int(mem_instance) / 100, ".2f"), mem_allocate, mem_instance, 'M')

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

    # 分配占用
    # flow_allocate = allocate[2]
    # # 实例最大占用,单位为Mbps
    # flow_instance = instance_max[3]
    # send_flow = 0.1 * 1024 * 1024
    # 发送流量组合数据
    # if int(send_flow) > 1024 * 1024:
    #     send_flow_merge = data_merge(format(int(send_flow) / 1024 / 1024, ".2f"), int(flow_allocate) / 8,
    #                                  int(flow_instance) / 8, 'MB')
    # elif int(send_flow) > 1024:
    #     send_flow_merge = data_merge(format(int(send_flow) / 1024, ".2f"), int(flow_allocate) * 1024 / 8,
    #                                  int(flow_instance) * 1024 / 8, 'KB')
    # else:
    #     send_flow_merge = data_merge(int(send_flow), int(int(flow_allocate) * 1024 * 1024 / 8),
    #                                  int(int(flow_instance) * 1024 * 1024 / 8), 'B')
    #
    # # 接收流量组合数据
    # if int(recv_flow) > 1024 * 1024:
    #     recv_flow_merge = data_merge(format(int(recv_flow) / 1024 / 1024, ".2f"), int(flow_allocate) / 8,
    #                                  int(flow_instance) / 8, 'MB')
    # elif int(recv_flow) > 1024:
    #     recv_flow_merge = data_merge(format(int(recv_flow) / 1024, ".2f"), int(flow_allocate) * 1024 / 8,
    #                                  int(flow_instance) * 1024 / 8, 'KB')
    # else:
    #     recv_flow_merge = data_merge(int(recv_flow), int(int(flow_allocate) * 1024 * 1024 / 8),
    #                                  int(int(flow_instance) * 1024 * 1024 / 8), 'B')

    # 服务器信息
    # sql_server = """select version,pattern,zone,run_company from zero_version where filename_uuid='%s';""" % uid
    # cursor.execute(sql_server)
    # server_info = cursor.fetchone()
    server_info = Version.objects.get(filename_uuid=uid)
    # 根据服务器版本查询出平台
    # sql_plat = "select plat from zero_add_version where version='%s';" % server_info[0]
    # cursor.execute(sql_plat)
    # plat = cursor.fetchone()
    plat = AddVersion.objects.get(version=server_info.version).plat
    rule_id = ServerNameRule.objects.get(server_name=server_name).id
    # 存在则更新,不存在插入
    server_update = ServerListUpdate(server_name=server_name, max_player=str(online) + '/' + server_max_player[-1],
                                     cpu=cpu, memory=memory, send_flow=send_flow, recv_flow=recv_flow,
                                     version=server_info.version, pattern=server_info.pattern, zone=server_info.zone,
                                     plat=plat, run_company=server_info.run_company, ip=ip, user=user, port=server_port,
                                     time=datetime.datetime.now(), account='', instance_id='1',
                                     is_activate=1, server_rule_id=rule_id)
    server_update.save()
    # if server_name[-1] in server_list_update_server_name:
    # update_sql = """update zero_server_list_update set max_player='%s',cpu='%s',memory='%s',send_flow='%s',
    #                 recv_flow='%s',version='%s',pattern='%s',zone='%s',plat='%s',run_company='%s',ip='%s',
    #                 user='%s',port='%s',account='%s',instance_name='%s',time=CURTIME() where server_name='%s';""" \
    #              % (
    #                  str(online) + '/' + server_max_player[-1], cpu_merge, mem_merge, send_flow_merge,
    #                  recv_flow_merge, server_info[0], server_info[1], server_info[2], plat[0], server_info[3],
    #                  ip, user, server_port[-1], '', '', server_name[-1])
    #
    # cursor.execute(update_sql)
    # # 不存在则插入
    # else:
    #     insert_sql = """insert into zero_server_list_update(server_name,max_player,cpu,memory,send_flow,recv_flow,
    #                 version,pattern,zone,plat,run_company,ip,user,port,time,account,instance_name,is_activate)
    #                 values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
    #                 CURTIME(),'%s','%s',1);""" % (server_name[-1], str(online) + '/' + server_max_player[-1],
    #                                               cpu_merge, mem_merge, send_flow_merge, recv_flow_merge,
    #                                               server_info[0], server_info[1],
    #                                               server_info[2], plat[0], server_info[3], ip, user, server_port[-1],
    #                                               '', '')
    #     cursor.execute(insert_sql)
    # 只有提交后数据库才会有数据
    # conn.commit()
    #
    # cursor.close()
    # # 关闭数据库连接
    # conn.close()
    # 关闭ssh远程连接
    ssh.close()


if __name__ == "__main__":
    # ip/user/实例名称/账户名称
    # insert_mysql('192.144.238.49,'root','192.144.238.49_server','沃德天·维森莫')
    insert_mysql('49.232.21.147', 'root', uid='')
