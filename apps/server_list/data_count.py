#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
# import os

from apps.server_list import mysql_count


def day_count(day, tyflag, start, dur, server):
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
    flag = 1
    # 能够多选,选多个服务器
    for name in server:
        onl, max_num, cpu_se_al, cpu_se_ins, cpu_allo, cpu_ins, memory_se_al, memory_se_ins, memory_allo, memory_ins, \
            send_flow_all, send_flow_ins, recv_flow_all, recv_flow_ins, flow_allo, flow_ins, temp_time_line = \
            mysql_count.search(day, tyflag, start, dur, name)
        # 将所选择的服务器数据对应时间的点相加
        if flag == 1:
            temp_onl = onl
            temp_cpu_se_al = cpu_se_al
            temp_cpu_se_ins = cpu_se_ins
            temp_memory_se_al = memory_se_al
            temp_memory_se_ins = memory_se_ins
            temp_send_flow_all = send_flow_all
            temp_send_flow_ins = send_flow_ins
            temp_recv_flow_all = recv_flow_all
            temp_recv_flow_ins = recv_flow_ins
            time_line = temp_time_line
            flag = 0
        else:
            # 先取并集
            # time_line = list(set(time_line).union(set(temp_time_line)))

            # 交集相加
            temp_inter = list(set(time_line).intersection(set(temp_time_line)))
            for temp in temp_inter:
                # 交集下标
                time_index = temp_time_line.index(temp)
                line_index = time_line.index(temp)
                # 数据相加
                temp_onl[line_index] += onl[time_index]
                temp_cpu_se_al[line_index] += cpu_se_al[time_index]
                temp_cpu_se_ins[line_index] += cpu_se_ins[time_index]
                temp_memory_se_al[line_index] += memory_se_al[time_index]
                temp_memory_se_ins[line_index] += memory_se_ins[time_index]
                temp_send_flow_all[line_index] += send_flow_all[time_index]
                temp_send_flow_ins[line_index] += send_flow_ins[time_index]
                temp_recv_flow_all[line_index] += recv_flow_all[time_index]
                temp_recv_flow_ins[line_index] += recv_flow_ins[time_index]
            # temp_time_line中有，但是time_line中没有的值，插入到相应数据列表的相应位置上
            temp_difference = list(set(temp_time_line).difference(set(time_line)))
            time_line += temp_difference
            time_line.sort()
            for temp in temp_difference:
                # time_line.append(temp)
                # time_line.sort()
                time_index = time_line.index(temp)
                line_index = temp_time_line.index(temp)
                temp_onl.insert(time_index, onl[line_index])
                temp_cpu_se_al.insert(time_index, cpu_se_al[line_index])
                temp_cpu_se_ins.insert(time_index, cpu_se_ins[line_index])
                temp_memory_se_al.insert(time_index, memory_se_al[line_index])
                temp_memory_se_ins.insert(time_index, memory_se_ins[line_index])
                temp_send_flow_all.insert(time_index, send_flow_all[line_index])
                temp_send_flow_ins.insert(time_index, send_flow_ins[line_index])
                temp_recv_flow_all.insert(time_index, recv_flow_all[line_index])
                temp_recv_flow_ins.insert(time_index, recv_flow_ins[line_index])
        max_player += max_num
        cpu_allocate += cpu_allo
        cpu_instance += cpu_ins
        memory_allocate += memory_allo
        memory_instance += memory_ins
        flow_allocate += flow_allo
        flow_instance += flow_ins
    # cpu，内存，流量占用分配/实例的比例
    online = [round(float(x)/len(server), 2) for x in temp_onl]
    cpu_allocate_series = [round(float(x)/len(server), 2) for x in temp_cpu_se_al]
    cpu_instance_series = [round(float(x) / len(server), 2) for x in temp_cpu_se_ins]
    memory_allocate_series = [round(float(x) / len(server), 2) for x in temp_memory_se_al]
    memory_instance_series = [round(float(x) / len(server), 2) for x in temp_memory_se_ins]
    send_flow_allocate_series = [round(float(x) / len(server), 2) for x in temp_send_flow_all]
    send_flow_instance_series = [round(float(x) / len(server), 2) for x in temp_send_flow_ins]
    recv_flow_allocate_series = [round(float(x) / len(server), 2) for x in temp_recv_flow_all]
    recv_flow_instance_series = [round(float(x) / len(server), 2) for x in temp_recv_flow_ins]
    
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
    day_count(day=7, tyflag=-2, start=0, dur=0, server='')
