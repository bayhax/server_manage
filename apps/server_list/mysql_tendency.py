#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
import pymysql
import datetime
# import numpy as np


# 数据趋势选择时间段时数据库查询语句
def ten_dur_sql(server_name, start, end):
    # 时间段
    sql = """select max_player,cpu,memory,send_flow,recv_flow,time from zero_server_list where server_name = '%s' 
            and time >= '%s' and time < '%s';""" % (server_name, start, end)
    return sql


# 数据趋势今日/昨日数据库查询语句
def ten_one_sql(server_name, tyflag):
    # 今日
    if tyflag == 0:
        sql = """select max_player,cpu,memory,send_flow,recv_flow,time from zero_server_list where server_name = '%s' 
                and DATEDIFF(time,NOW())=0;""" % server_name
    # 昨日
    else:
        sql = """select max_player,cpu,memory,send_flow,recv_flow,time from zero_server_list where server_name = '%s' 
                and DATEDIFF(time,NOW())=-1;""" % server_name
    return sql


# 数据趋势近7日/近30日数据库查询语句
def ten_day_sql(server_name, date):
    # 近七日
    sql = """select max_player,cpu,memory,send_flow,recv_flow,time from zero_server_list where server_name = '%s' 
                and DATEDIFF(time,NOW())='%s';""" % (server_name, date)
    return sql


# 将数据库查询出的结果进行整理
def handle_data(count_server):
    time_line = []
    temp_onl = []
    temp_cpu_se_al = []
    temp_cpu_se_ins = []
    temp_memory_se_al = []
    temp_memory_se_ins = []
    temp_send_flow_all = []
    temp_send_flow_ins = []
    temp_recv_flow_all = []
    temp_recv_flow_ins = []
    for i in range(0, 24):
        for j in range(0, 60, 5):
            temp_onl.append(0.0)
            temp_cpu_se_al.append(0.0)
            temp_cpu_se_ins.append(0.0)
            temp_memory_se_al.append(0.0)
            temp_memory_se_ins.append(0.0)
            temp_send_flow_all.append(0.0)
            temp_send_flow_ins.append(0.0)
            temp_recv_flow_all.append(0.0)
            temp_recv_flow_ins.append(0.0)
            if i < 10:
                if j < 10:
                    time_line.append('0%d:0%d' % (i, j))
                else:
                    time_line.append('0%d:%d' % (i, j))
            else:
                if j < 10:
                    time_line.append('%d:0%d' % (i, j))
                else:
                    time_line.append('%d:%d' % (i, j))
    # 取在线人数/最大人数等信息(循环是如果某个时段人为或者某种原因多插入了一条数据，则取最后一次数据为有效值，日后还可作为判断服务器异常情况)
    for ser in count_server:
        # print(ser[5].strftime('%H:%M'))
        # print(ser[5].strftime('%H:%M'), time_line)
        if ser[5].strftime('%H:%M') in time_line:
            index = time_line.index(ser[5].strftime('%H:%M'))
            temp_onl[index] = int((ser[0].split('/')[0]))
            temp_cpu_se_al[index] = ser[1]
            temp_cpu_se_ins[index] = ser[1]
            temp_memory_se_al[index] = ser[2]
            temp_memory_se_ins[index] = ser[2]
            temp_send_flow_all[index] = ser[3]
            temp_send_flow_ins[index] = ser[3]
            temp_recv_flow_all[index] = ser[4]
            temp_recv_flow_ins[index] = ser[4]
    return temp_onl, temp_cpu_se_al, temp_cpu_se_ins, temp_memory_se_al, temp_memory_se_ins,\
        temp_send_flow_all, temp_send_flow_ins, temp_recv_flow_all, temp_recv_flow_ins,


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
    # begin = '2020-03-04'

    # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    db = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    # 数据查询段，起始s，结束e，规定内层时间段起止时间
    # dur为0，不是搜寻日期所进行的查询，而是今日/昨日/近七日/近30日，判断day还有tyflag
    if dur == 0:
        # 昨日/今日
        if day == 0:
            s = 0
            e = 1
        # 近7日或者近30日
        else:
            s = 1 - day
            e = 1
    # 搜寻日期，时间段查询，
    else:
        s = 0
        e = dur
        # begin = datetime.datetime.strptime(start, '%Y-%m-%d')
    temp_op = [0.0] * 288
    temp_csa = [0.0] * 288
    temp_csi = [0.0] * 288
    temp_msa = [0.0] * 288
    temp_msi = [0.0] * 288
    temp_sfsa = [0.0] * 288
    temp_sfsi = [0.0] * 288
    temp_rfsa = [0.0] * 288
    temp_rfsi = [0.0] * 288
    for i in range(s, e):
        if dur == 0:
            # 昨日/今日
            if day == 0:
                sql = ten_one_sql(server_name, tyflag)
            # 近7日或者近30日
            else:
                sql = ten_day_sql(server_name, i)
        # 搜寻日期，时间段查询，
        else:
            begin = datetime.datetime.strptime(start, '%Y-%m-%d')
            delta = datetime.timedelta(days=1)
            end = begin + delta
            sql = ten_dur_sql(server_name, begin, end)
            start = end.strftime('%Y-%m-%d')
        # start = datetime.datetime.now()
        cursor.execute(sql)
        count_server = cursor.fetchall()
        # end = datetime.datetime.now()
        # print(end-start)
        temp_online_player, temp_cpu_self_allocate, temp_cpu_self_instance, temp_memory_self_allocate, \
            temp_memory_self_instance, temp_send_flow_self_allocate, temp_send_flow_self_instance, \
            temp_recv_flow_self_allocate, temp_recv_flow_self_instance = handle_data(count_server)

        # end2 = datetime.datetime.now()

        for j in range(288):
            temp_op[j] += temp_online_player[j]
            temp_csa[j] += temp_cpu_self_allocate[j]
            temp_csi[j] += temp_cpu_self_instance[j]
            temp_msa[j] += temp_memory_self_allocate[j]
            temp_msi[j] += temp_memory_self_instance[j]
            temp_sfsa[j] += temp_send_flow_self_allocate[j]
            temp_sfsi[j] += temp_send_flow_self_instance[j]
            temp_rfsa[j] += temp_recv_flow_self_allocate[j]
            temp_rfsi[j] += temp_send_flow_self_instance[j]
    # 取平均值
    for i in range(0, 288):
        online_player.append(round(temp_op[i] / (e - s), 2))
        cpu_self_allocate.append(round(temp_csa[i] / (e - s), 2))
        cpu_self_instance.append(round(temp_csi[i] / (e - s), 2))
        memory_self_allocate.append(round(temp_msa[i] / (e - s), 2))
        memory_self_instance.append(round(temp_msi[i] / (e - s), 2))
        send_flow_self_allocate.append(round(temp_sfsa[i] / (e - s), 2))
        send_flow_self_instance.append(round(temp_sfsi[i] / (e - s), 2))
        recv_flow_self_allocate.append(round(temp_rfsa[i] / (e - s), 2))
        recv_flow_self_instance.append(round(temp_sfsi[i] / (e - s), 2))
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
        send_flow_self_instance, recv_flow_self_allocate, recv_flow_self_instance, flow_allocate, flow_instance


if __name__ == '__main__':
    search(day=7, tyflag=-2, start='2020-03-12', dur=4, server_name='删档测试二服')
