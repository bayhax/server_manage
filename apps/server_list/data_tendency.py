#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
# import os
# import datetime
from apps.server_list import mysql_tendency


def tendency(day, tyflag, start, dur, server):

    max_player = 0  # 最大人数
    cpu_allocate = 0  # 分配cpu
    cpu_instance = 0  # 实例最大cpu
    memory_allocate = 0  # 内存分配
    memory_instance = 0  # 实例最大内存
    flow_allocate = 0  # 流量分配
    flow_instance = 0  # 实例最大流量分配
    temp_onl = []
    temp_cpu_se_al = []
    temp_cpu_se_ins = []
    temp_memory_se_al = []
    temp_memory_se_ins = []
    temp_send_flow_all = []
    temp_send_flow_ins = []
    temp_recv_flow_all = []
    temp_recv_flow_ins = []
    time_line = []
    # 生成time_line数据
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
    # 能够多选,选多个服务器
    for name in server:
        onl, max_num, cpu_se_al, cpu_se_ins, cpu_allo, cpu_ins, memory_se_al, memory_se_ins, memory_allo, memory_ins, \
            send_flow_all, send_flow_ins, recv_flow_all, recv_flow_ins, flow_allo, flow_ins = \
            mysql_tendency.search(day, tyflag, start, dur, name)

        # 将所选择的服务器数据相加
        temp_onl = [i+j for i, j in zip(temp_onl, onl)]
        temp_cpu_se_al = [i+j for i, j in zip(temp_cpu_se_al, cpu_se_al)]
        temp_cpu_se_ins = [i+j for i, j in zip(temp_cpu_se_ins, cpu_se_ins)]
        temp_memory_se_al = [i+j for i, j in zip(temp_memory_se_al, memory_se_al)]
        temp_memory_se_ins = [i+j for i, j in zip(temp_memory_se_ins, memory_se_ins)]
        temp_send_flow_all = [i+j for i, j in zip(temp_send_flow_all, send_flow_all)]
        temp_send_flow_ins = [i+j for i, j in zip(temp_send_flow_ins, send_flow_ins)]
        temp_recv_flow_all = [i+j for i, j in zip(temp_recv_flow_all, recv_flow_all)]
        temp_recv_flow_ins = [i+j for i, j in zip(temp_recv_flow_ins, recv_flow_ins)]
        max_player += max_num
        cpu_allocate += cpu_allo
        cpu_instance += cpu_ins
        memory_allocate += memory_allo
        memory_instance += memory_ins
        flow_allocate += flow_allo
        flow_instance += flow_ins

    # 取平均值
    temp_onl = [round(x/len(server), 2) for x in temp_onl]
    temp_cpu_se_al = [round(x/len(server), 2) for x in temp_cpu_se_al]
    temp_cpu_se_ins = [round(x / len(server), 2) for x in temp_cpu_se_ins]
    temp_memory_se_al = [round(x / len(server), 2) for x in temp_memory_se_al]
    temp_memory_se_ins = [round(x / len(server), 2) for x in temp_memory_se_ins]
    temp_send_flow_all = [round(x / len(server), 2) for x in temp_send_flow_all]
    temp_send_flow_ins = [round(x / len(server), 2) for x in temp_send_flow_ins]
    temp_recv_flow_all = [round(x / len(server), 2) for x in temp_recv_flow_all]
    temp_recv_flow_ins = [round(x / len(server), 2) for x in temp_recv_flow_ins]
    # cpu，内存，流量占用分配/实例的比例
    online = temp_onl
    cpu_allocate_series = temp_cpu_se_al
    cpu_instance_series = temp_cpu_se_ins
    memory_allocate_series = temp_memory_se_al
    memory_instance_series = temp_memory_se_ins
    send_flow_allocate_series = temp_send_flow_all
    send_flow_instance_series = temp_send_flow_ins
    recv_flow_allocate_series = temp_recv_flow_all
    recv_flow_instance_series = temp_recv_flow_ins

    # series数据
    series = [{'name': '在线人数', 'type': 'line', 'smooth': 'true', 'data': online},
              {'name': 'cpu占用率-分配', 'type': 'line', 'smooth': 'true', 'data': cpu_allocate_series},
              {'name': 'cpu占用率-实例', 'type': 'line', 'smooth': 'true', 'data': cpu_instance_series},
              {'name': '内存占用-分配', 'type': 'line', 'smooth': 'true', 'data': memory_allocate_series},
              {'name': '内存占用-实例', 'type': 'line', 'smooth': 'true', 'data': memory_instance_series},
              {'name': '发送流量占用-分配', 'type': 'line', 'smooth': 'true', 'data': send_flow_allocate_series},
              {'name': '发送流量占用-实例', 'type': 'line', 'smooth': 'true', 'data': send_flow_instance_series},
              {'name': '接收流量占用-分配', 'type': 'line', 'smooth': 'true', 'data': recv_flow_allocate_series},
              {'name': '接收流量占用-实例', 'type': 'line', 'smooth': 'true', 'data': recv_flow_instance_series}]

    return series, max_player, cpu_allocate, cpu_instance, memory_allocate, memory_instance, \
        flow_allocate, flow_instance, time_line


if __name__ == "__main__":
    tendency(day=7, tyflag=-2, start=0, dur=0, server='')
