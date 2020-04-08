#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
import pymysql
import datetime
# import numpy as np


# 数据趋势选择时间段时数据库查询语句
def ten_dur_sql(server_name, start, end, starth, endh, startm, endm):
    # 时间段
    sql = """select max_player,cpu,memory,send_flow,recv_flow from zero_server_list where server_name = '%s' 
            and time >= '%s' and time < '%s' and hour(time) >= '%s' and hour(time) < '%s' and minute(time) >= '%s'
            and minute(time) < '%s';""" % (server_name, start, end, starth, endh, startm, endm)
    return sql


# 数据趋势今日/昨日数据库查询语句
def ten_one_sql(server_name, tyflag, start, end, startm, endm):
    # 今日
    if tyflag == 0:
        sql = """select max_player,cpu,memory,send_flow,recv_flow from zero_server_list where server_name = '%s' 
                and DATEDIFF(time,NOW())=0 and hour(time)>='%s' and hour(time)<'%s' and minute(time) >= '%s' and minute(time) < '%s';""" \
              % (server_name, start, end, startm, endm)
    # 昨日
    else:
        sql = """select max_player,cpu,memory,send_flow,recv_flow from zero_server_list where server_name = '%s' 
                and DATEDIFF(time,NOW())=-1 and hour(time)>='%s' and hour(time)<'%s' and minute(time) >= '%s' and minute(time) < '%s';""" \
              % (server_name, start, end, startm, endm)
    return sql


# 数据趋势近7日/近30日数据库查询语句
def ten_day_sql(server_name, date, start, end, startm, endm):
    # 近七日/近30日
    sql = """select max_player,cpu,memory,send_flow,recv_flow from zero_server_list where server_name = '%s' 
            and DATEDIFF(time,NOW())='%s' and hour(time)>='%s' and hour(time)<'%s' and minute(time)>='%s'
            and minute(time)<'%s';""" % (server_name, date, start, end, startm, endm)
    return sql


# 将数据库查询出的结果进行整理
def handle_data(count_server):
    cpu_self_allocate_temp = 0.0
    cpu_self_instance_temp = 0.0
    memory_self_allocate_temp = 0.0
    memory_self_instance_temp = 0.0
    send_flow_self_allocate_temp = 0.0
    send_flow_self_instance_temp = 0.0
    recv_flow_self_allocate_temp = 0.0
    recv_flow_self_instance_temp = 0.0
    online_player_temp = 0.0

    # 取在线人数/最大人数等信息(循环是如果某个时段人为或者某种原因多插入了一条数据，则取最后一次数据为有效值，日后还可作为判断服务器异常情况)
    for ser in count_server:
        # 如果该元组的该位置没有数据，则放入默认数据，（防止数据运算出错）
        # 在线人数
        online_player_temp = int((ser[0].split('/')[0]))

        # cpu占用
        cpu_self_allocate_temp = ser[1].split('-')[0].split('/')[0].replace('%', '')
        cpu_self_instance_temp = ser[1].split('-')[0].split('/')[1].replace('%', '')

        # 内存占用
        memory_self_allocate_temp = ser[2].split('-')[0].split('/')[0].replace('%', '')
        memory_self_instance_temp = ser[2].split('-')[0].split('/')[1].replace('%', '')

        # 发送流量占用
        send_flow_self_allocate_temp = ser[3].split('-')[0].split('/')[0].replace('%', '')
        send_flow_self_instance_temp = ser[3].split('-')[0].split('/')[1].replace('%', '')

        # 接收流量占用
        recv_flow_self_allocate_temp = ser[4].split('-')[0].split('/')[0].replace('%', '')
        recv_flow_self_instance_temp = ser[4].split('-')[0].split('/')[1].replace('%', '')

    return online_player_temp, cpu_self_allocate_temp, cpu_self_instance_temp, memory_self_allocate_temp, \
        memory_self_instance_temp, send_flow_self_allocate_temp, send_flow_self_instance_temp, \
        recv_flow_self_allocate_temp, recv_flow_self_instance_temp


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
    begin = '2020-03-04'

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
        begin = datetime.datetime.strptime(start, '%Y-%m-%d')
    # 数据采集时段一共288个，每五分钟一次
    for c in range(0, 24):
        # 每五分钟
        for j in range(0, 60, 5):
            temp_op = 0.0
            temp_csa = 0.0
            temp_csi = 0.0
            temp_msa = 0.0
            temp_msi = 0.0
            temp_sfsa = 0.0
            temp_sfsi = 0.0
            temp_rfsa = 0.0
            temp_rfsi = 0.0
            # 每次将起始日期初始化，很重要，不然数据是错的
            if dur != 0:
                start = begin
            # 时间段的数据查询
            for i in range(s, e):
                # 搜寻时间段
                if dur != 0:
                    delta = datetime.timedelta(days=1)
                    end = start + delta
                    sql = ten_dur_sql(server_name, start, end, c, c + 1, j, j + 5)
                    start = end
                    cursor.execute(sql)
                    count_server = cursor.fetchall()
                    temp_online_player, temp_cpu_self_allocate, temp_cpu_self_instance, temp_memory_self_allocate, \
                        temp_memory_self_instance, temp_send_flow_self_allocate, temp_send_flow_self_instance, \
                        temp_recv_flow_self_allocate, temp_recv_flow_self_instance = handle_data(count_server)
                # 不是艘寻时间段
                else:
                    # 今日/昨日
                    if day == 0:
                        sql = ten_one_sql(server_name, tyflag, c, c + 1, j, j + 5)
                        cursor.execute(sql)
                        count_server = cursor.fetchall()
                        temp_online_player, temp_cpu_self_allocate, temp_cpu_self_instance, temp_memory_self_allocate, \
                            temp_memory_self_instance, temp_send_flow_self_allocate, temp_send_flow_self_instance, \
                            temp_recv_flow_self_allocate, temp_recv_flow_self_instance = handle_data(count_server)
                    # 近7日/近30日
                    else:
                        sql = ten_day_sql(server_name, i, c, c + 1, j, j + 5)
                        cursor.execute(sql)
                        count_server = cursor.fetchall()
                        temp_online_player, temp_cpu_self_allocate, temp_cpu_self_instance, temp_memory_self_allocate, \
                            temp_memory_self_instance, temp_send_flow_self_allocate, temp_send_flow_self_instance, \
                            temp_recv_flow_self_allocate, temp_recv_flow_self_instance = handle_data(count_server)
                temp_op += float(temp_online_player)
                temp_csa += float(temp_cpu_self_allocate)
                temp_csi += float(temp_cpu_self_instance)
                temp_msa += float(temp_memory_self_allocate)
                temp_msi += float(temp_memory_self_instance)
                temp_sfsa += float(temp_send_flow_self_allocate)
                temp_sfsi += float(temp_send_flow_self_instance)
                temp_rfsa += float(temp_recv_flow_self_allocate)
                temp_rfsi += float(temp_send_flow_self_instance)
            # 取平均值
            online_player.append(round(temp_op / (e - s), 2))
            cpu_self_allocate.append(round(temp_csa / (e - s), 2))
            cpu_self_instance.append(round(temp_csi / (e - s), 2))
            memory_self_allocate.append(round(temp_msa / (e - s), 2))
            memory_self_instance.append(round(temp_msi / (e - s), 2))
            send_flow_self_allocate.append(round(temp_sfsa / (e - s), 2))
            send_flow_self_instance.append(round(temp_sfsi / (e - s), 2))
            recv_flow_self_allocate.append(round(temp_rfsa / (e - s), 2))
            recv_flow_self_instance.append(round(temp_sfsi / (e - s), 2))

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
    flow_instance = int(info[0].split('/')[3].replace('Mbps', ''))
    # 关闭数据库连接
    cursor.close()
    db.close()
    return online_player, max_player, cpu_self_allocate, cpu_self_instance, cpu_allocate, cpu_instance, \
        memory_self_allocate, memory_self_instance, memory_allocate, memory_instance, send_flow_self_allocate, \
        send_flow_self_instance, recv_flow_self_allocate, recv_flow_self_instance, flow_allocate, flow_instance


if __name__ == '__main__':
    search(day=7, tyflag=-2, start='2020-03-12', dur=4, server_name='删档测试二服')
