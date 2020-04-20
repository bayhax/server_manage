#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import os
import re
import paramiko
import pymysql


def data_merge(itself, allocate, instance, signal):
    # 本身占用/分配占用
    self_alloc = str(format(float(itself) / float(allocate) * 100, '.2f'))
    # 本身占用/实例最大占用
    self_ins = str(format(float(itself) / float(instance) * 100, '.2f'))

    # 组合数据
    merge = self_alloc + "%/" + self_ins + "%-" + str(itself) + signal + "/" + str(allocate) + signal + "/" + \
            str(instance) + signal
    return merge


def insert_mysql(ip, user, instance, account_name):
    print(ip,user)
    server_max_player = []  # 服务器最大在线人数，列表存起来对应每个服务器
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
    conn = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()
    server_list_update_server_name = []
    # zero_server_list_update表中所有服务器名称
    sql = """select server_name from zero_server_list_update;"""
    cursor.execute(sql)
    data = cursor.fetchall()
    for d in data:
        server_list_update_server_name.append(d[0])
    # 定时任务获取的文件名
    filename = '/home/time_task/merge_info_' + ip + '.txt'
    # 根据ip地址读取time_task文件夹下的相应文件
    with open(filename, 'r') as f:
        info = f.readlines()
    for data in info:
        it_server = data.split(' ')
        server_name = it_server[0]
        # 如果该服务器is_activate状态标志为0，则continue,不插入数据。
        search_sql = "select is_activate from zero_server_list_update where server_name='%s';" % server_name
        cursor.execute(search_sql)
        is_activate = cursor.fetchone()[0]
        if is_activate == 0:
            continue
        server_port = it_server[1]
        # 最大人数取值出现错误，则用0代替，表示出错
        if it_server[2] == '':
            server_max_player = 0            
        server_max_player = it_server[2]
        # 根据服务器名称在zero_version表中取出模式名称
        sql_pattern = """select pattern from zero_version where server_name = '%s';""" % server_name
        cursor.execute(sql_pattern)
        pattern = cursor.fetchone()
        pattern = pattern[0]
        # 在zero_pattern表中取出该模式的分配信息,结果为元组
        sql_allocate = """select cpu_num,memory_num,flow_num from zero_pattern where pattern='%s';""" % pattern
        # print(sql_allocate)
        cursor.execute(sql_allocate)
        allocate = cursor.fetchone()
        # 根据ip在zero_ins_type表中取出ins_type，即实例最大
        sql_instance = "select ins_type from zero_ins_type where ip='%s';" % ip
        cursor.execute(sql_instance)
        instance_max = cursor.fetchone()
        # 利用正则表达式将实例最大配置的数字取出来
        instance_max = re.findall(r"\d+\.?\d*", instance_max[0])
        # pid = int(it_server[3])
        if it_server[4] == '' or len(it_server[4]) > 4:
            print('没有拿到在线人数，可能服务器未完全开启或连接超时。')
            online = 0
        else:
            online = int(it_server[4])
        cpu = it_server[5]
        # 分配占用,int
        cpu_allocate = allocate[0]

        # 实例最大占用,str
        cpu_instance = instance_max[0]

        # cpu组合数据
        # print(type(cpu),type(cpu_allocate),type(cpu_instance))
        cpu_merge = data_merge(format(float(cpu) * int(cpu_instance) / 100, ".2f"), cpu_allocate, cpu_instance, '')
        memory = it_server[6]
        # 分配内存,int
        mem_allocate = allocate[1]

        # 实例最大占用,str
        mem_instance = instance_max[1]

        # 内存组合数据
        mem_merge = data_merge(format(float(memory) * int(mem_instance) / 100, ".2f"), mem_allocate, mem_instance, 'G')

        # 发送流量占用
        send_flow = it_server[7]
        # 接收流量占用
        recv_flow = it_server[8]

        # 分配占用
        flow_allocate = allocate[2]
        # 实例最大占用,单位为Mbps
        flow_instance = instance_max[3]
        # send_flow = 0.1 * 1024 * 1024
        # 发送流量组合数据
        if int(send_flow) > 1024 * 1024:
            send_flow_merge = data_merge(format(int(send_flow) / 1024 / 1024, ".2f"), int(flow_allocate) / 8,
                                         int(flow_instance) / 8, 'MB')
        elif int(send_flow) > 1024:
            send_flow_merge = data_merge(format(int(send_flow) / 1024, ".2f"), int(flow_allocate) * 1024 / 8,
                                         int(flow_instance) * 1024 / 8, 'KB')
        else:
            send_flow_merge = data_merge(int(send_flow), int(int(flow_allocate) * 1024 * 1024 / 8),
                                         int(int(flow_instance) * 1024 * 1024 / 8), 'B')

        # 接收流量组合数据
        if int(recv_flow) > 1024 * 1024:
            recv_flow_merge = data_merge(format(int(recv_flow) / 1024 / 1024, ".2f"), int(flow_allocate) / 8,
                                         int(flow_instance) / 8, 'MB')
        elif int(recv_flow) > 1024:
            recv_flow_merge = data_merge(format(int(recv_flow) / 1024, ".2f"), int(flow_allocate) * 1024 / 8,
                                         int(flow_instance) * 1024 / 8, 'KB')
        else:
            recv_flow_merge = data_merge(int(recv_flow), int(int(flow_allocate) * 1024 * 1024 / 8),
                                         int(int(flow_instance) * 1024 * 1024 / 8), 'B')

        # print(send_flow, flow_allocate, flow_instance, send_flow_merge)
        # 服务器信息
        sql_server = """select version,pattern,zone,run_company from zero_version where server_name='%s';""" % \
                     server_name
        cursor.execute(sql_server)
        server_info = cursor.fetchone()
        # 根据服务器版本查询出平台
        sql_plat = "select plat from zero_add_version where version='%s';" % server_info[0]
        cursor.execute(sql_plat)
        plat = cursor.fetchone()

        sql = """insert into zero_server_list(server_name,max_player,cpu,memory,send_flow,recv_flow,version,pattern,
                        zone,plat,run_company,ip,user,port,time,account,instance_name,is_activate)
                        values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',CURTIME(),'%s','%s',1);
                        """ % (server_name, str(online) + '/' + server_max_player, cpu_merge, mem_merge,
                               send_flow_merge, recv_flow_merge, server_info[0], server_info[1], server_info[2],
                               plat[0], server_info[3], ip, user, server_port, account_name, instance)
        # print(sql)
        cursor.execute(sql)

        # 存在则更新
        if server_name in server_list_update_server_name:
            update_sql = """update zero_server_list_update set max_player='%s',cpu='%s',memory='%s',send_flow='%s',
                                    recv_flow='%s', version='%s',pattern='%s',zone='%s',plat='%s',run_company='%s',
                                    ip='%s', user='%s',port='%s',account='%s',instance_name='%s',time=CURTIME() 
                                    where server_name='%s';""" % (str(online) + '/' + server_max_player, cpu_merge,mem_merge, send_flow_merge, recv_flow_merge,server_info[0], 
                                                                  server_info[1], server_info[2],plat[0], server_info[3], ip, user, server_port, account_name, instance, server_name)
            cursor.execute(update_sql)
        # 不存在则插入
        else:
            insert_sql = """insert into zero_server_list_update(server_name,max_player,cpu,memory,send_flow,recv_flow,
                                    version,pattern,zone,plat,run_company,ip,user,port,time,account,instance_name,is_activate)
                                    values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',CURTIME(),'%s','%s',1);
                                """ % (server_name, str(online) + '/' + server_max_player, cpu_merge, mem_merge,
                                       send_flow_merge, recv_flow_merge, server_info[0], server_info[1], server_info[2],
                                       plat[0], server_info[3], ip, user, server_port, account_name, instance)
            cursor.execute(insert_sql)
    # 只有提交后数据库才会有数据
    conn.commit()

    cursor.close()
    # 关闭数据库连接
    conn.close()
    # 关闭ssh远程连接
    ssh.close()


if __name__ == "__main__":
    # ip/user/实例名称/账户名称
    # insert_mysql('192.144.238.49', 'root', '192.144.238.49_server', '沃德天·维森莫')
    insert_mysql('49.232.21.147', 'root', '49.232.21.147_server', '孙')
