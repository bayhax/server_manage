#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
import pymysql
import datetime


# 数据统计选择时间段时数据库查询语句
def cou_dur_sql(server_name, start, end):
    # 时间段
    sql = """select max_player,cpu,memory,send_flow,recv_flow,time from zero_server_list where server_name = '%s' and 
        time >= '%s' and time <= '%s';""" % (server_name, start, end)
    return sql


# 数据统计今日/昨日数据库查询语句
def cou_one_sql(server_name, tyflag, start, end):
    # 今日
    if tyflag == 0:
        sql = """select max_player,cpu,memory,send_flow,recv_flow,time from zero_server_list where server_name = '%s' 
            and DATEDIFF(time,NOW())=0 and time >= DATE_ADD(CURDATE(),INTERVAL '%s' HOUR) 
            and time <= DATE_ADD(CURDATE(), INTERVAL '%s' HOUR);""" % (server_name, start, end)
    else:
        sql = """select max_player,cpu,memory,send_flow,recv_flow from zero_server_list where server_name = '%s' 
            and DATEDIFF(time,NOW())=-1 and time >= DATE_ADD(CURDATE(),INTERVAL '%s' HOUR) 
            and time <= DATE_ADD(CURDATE(), INTERVAL '%s' HOUR);""" % (server_name, start, end)

    return sql


# 数据统计近7日/近30日数据库查询语句
def cou_day_sql(server_name, date):
    # 近7日/近30日
    sql = """select max_player,cpu,memory,send_flow,recv_flow,time from zero_server_list where server_name = '%s' 
    and DATEDIFF(time,NOW())='%s';""" % (server_name, date)

    return sql


# 将数据库查询出的结果进行整理
def handle_data(count_server):
    cpu_self_allocate_temp = []
    cpu_self_instance_temp = []
    memory_self_allocate_temp = []
    memory_self_instance_temp = []
    send_flow_self_allocate_temp = []
    send_flow_self_instance_temp = []
    recv_flow_self_allocate_temp = []
    recv_flow_self_instance_temp = []
    online_player_temp = []
    time_temp = []
    # 取在线人数/最大人数等信息
    for ser in count_server:
        # 如果该元组的该位置没有数据，则放入默认数据，（防止数据运算出错）
        # 在线人数
        if ser[0] == '':
            online_player_temp.append(0)
        else:
            online_player_temp.append(int(ser[0].split('/')[0]))

        # cpu占用
        if ser[1] == '':
            cpu_self_allocate_temp.append(0.0)
            cpu_self_instance_temp.append(0.0)
        else:
            cpu_self_allocate_temp.append(ser[1])
            cpu_self_instance_temp.append(ser[1])

        # 内存占用
        if ser[2] == '':
            memory_self_allocate_temp.append(0.0)
            memory_self_instance_temp.append(0.0)
        else:
            memory_self_allocate_temp.append(ser[2])
            memory_self_instance_temp.append(ser[2])

        # 发送流量占用
        if ser[3] == '':
            send_flow_self_allocate_temp.append(0.0)
            send_flow_self_instance_temp.append(0.0)
        else:
            send_flow_self_allocate_temp.append(ser[3])
            send_flow_self_instance_temp.append(ser[3])

        # 接收流量占用
        if ser[4] == '':
            recv_flow_self_allocate_temp.append(0.0)
            recv_flow_self_instance_temp.append(0.0)
        else:
            recv_flow_self_allocate_temp.append(ser[4])
            recv_flow_self_instance_temp.append(ser[4])

        # 时间
        if ser[5] == '':
            time_temp.append(0.0)
        else:
            time_temp.append(ser[5].strftime('%Y-%m-%d %H:%M'))

    return online_player_temp, cpu_self_allocate_temp, cpu_self_instance_temp, memory_self_allocate_temp, \
        memory_self_instance_temp, send_flow_self_allocate_temp, send_flow_self_instance_temp, \
        recv_flow_self_allocate_temp, recv_flow_self_instance_temp, time_temp


# flag标志(统计/趋势),day近几日，start起始日期，end结束日期，dur间隔，server_name服务器名称,tyflag是今日还是昨日,0今日，-1昨日。
def search(day, tyflag, start, dur, server_name):
    # cpu列表/内存列表/发送流量列表/接收流量列表/再现人数列表/cpu自身占用列表/内存自身占用列表/发送流量数据列表/接收流量数据列表/
    # 时间段内cpu平均值/时间段内内存占用平均值/时间段内发送流量平均值/时间段内接收流量平均值/在线人数/数据库查询结果临时数据/开始日期临时数据
    cpu_self_allocate = []
    cpu_self_instance = []
    memory_self_allocate = []
    memory_self_instance = []
    send_flow_self_allocate = []
    send_flow_self_instance = []
    recv_flow_self_allocate = []
    recv_flow_self_instance = []
    online_player = []
    time_line = []
    # begin = '2020-03-04'

    # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    db = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    # dur为0，不是搜寻日期所进行的查询，而是今日/昨日/近七日/近30日，判断day还有tyflag
    if dur == 0:
        # 非近七日/近30日
        if day == 0:
            # 今日或者昨日
            s = 0
            e = 24
        # 近7日或者近30日
        else:
            s = 1 - day
            e = 1
    # 搜寻日期，时间段查询，
    else:
        s = 0
        e = dur
        begin = datetime.datetime.strptime(start, '%Y-%m-%d')
    if dur != 0:
        start = begin
    # 数据统计
    for i in range(s, e):
        # 搜寻时间段
        if dur != 0:
            delta = datetime.timedelta(days=1)
            end = start + delta
            sql = cou_dur_sql(server_name, start, end)
            start = end
            cursor.execute(sql)
            count_server = cursor.fetchall()
            temp_online_player, temp_cpu_self_allocate, temp_cpu_self_instance, temp_memory_self_allocate, \
                temp_memory_self_instance, temp_send_flow_self_allocate, temp_send_flow_self_instance, \
                temp_recv_flow_self_allocate, temp_recv_flow_self_instance, temp_time = handle_data(count_server)
        # 不是艘寻时间段
        else:
            # 今日/昨日
            if day == 0:
                sql = cou_one_sql(server_name, tyflag, i, i + 1)
                cursor.execute(sql)
                count_server = cursor.fetchall()
                temp_online_player, temp_cpu_self_allocate, temp_cpu_self_instance, temp_memory_self_allocate, \
                    temp_memory_self_instance, temp_send_flow_self_allocate, temp_send_flow_self_instance, \
                    temp_recv_flow_self_allocate, temp_recv_flow_self_instance, temp_time = handle_data(count_server)
            # 近7日/近30日
            else:
                sql = cou_day_sql(server_name, i)
                cursor.execute(sql)
                count_server = cursor.fetchall()
                temp_online_player, temp_cpu_self_allocate, temp_cpu_self_instance, temp_memory_self_allocate, \
                    temp_memory_self_instance, temp_send_flow_self_allocate, temp_send_flow_self_instance, \
                    temp_recv_flow_self_allocate, temp_recv_flow_self_instance, temp_time = handle_data(count_server)
        # 列表相加
        online_player += temp_online_player
        cpu_self_allocate += temp_cpu_self_allocate
        cpu_self_instance += temp_cpu_self_instance
        memory_self_allocate += temp_memory_self_allocate
        memory_self_instance += temp_memory_self_instance
        send_flow_self_allocate += temp_send_flow_self_allocate
        send_flow_self_instance += temp_send_flow_self_instance
        recv_flow_self_allocate += temp_recv_flow_self_allocate
        recv_flow_self_instance += temp_send_flow_self_instance
        time_line += temp_time
    # 根据服务器名称搜寻出模式
    sql_pattern = "select pattern from zero_version where server_name = '%s';" % server_name
    cursor.execute(sql_pattern)
    pattern = cursor.fetchone()
    # 在模式表中查出该模式的配置信息，最大在线人数，分配cpu,实例的最大cpu等信息。
    sql_allo_ins = "select ins_type,player_num,cpu_num,memory_num,flow_num from zero_pattern where pattern='%s';" \
                   % pattern[0]
    cursor.execute(sql_allo_ins)
    info = cursor.fetchone()
    # 查询结果，元组，实例类型，最大在线人数，分配cpu,分配内存,分配流量
    max_player = int(info[1])
    cpu_allocate = int(info[2])
    cpu_instance = int(info[0].split('/')[0].replace('核', ''))
    memory_allocate = int(info[3])
    memory_instance = int(info[0].split('/')[1].replace('G', ''))
    # 流量
    flow_allocate = int(info[4])
    flow_instance = int(info[0].split('/')[2].replace('Mbps', ''))
    # 关闭数据库连接
    cursor.close()
    db.close()
    return online_player, max_player, cpu_self_allocate, cpu_self_instance, cpu_allocate, cpu_instance, \
        memory_self_allocate, memory_self_instance, memory_allocate, memory_instance, send_flow_self_allocate, \
        send_flow_self_instance, recv_flow_self_allocate, recv_flow_self_instance, flow_allocate, flow_instance, \
        time_line


if __name__ == '__main__':
    search(day=7, tyflag=-2, start='2020-03-12', dur=4, server_name='删档测试二服')
