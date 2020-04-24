# ！/root/.virtualenvs/server/bin/python3
# -*- coding:utf-8 -*-
# @Time: 4/22/20 3:16 PM
# @Author:bayhax
# @Filename: tasks.py
from __future__ import absolute_import
from celery import shared_task
from django_redis import get_redis_connection

import datetime
import json
import os
import re
import time
import pymysql

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.cvm.v20170312 import cvm_client, models

from cloud_user.models import Account
from config.models import Version, Pattern, AddVersion
from server_list.models import ServerNameRule, ServerPid, InsType, ServerList


def data_merge(itself, allocate, instance, signal):
    # 本身占用/分配占用
    self_alloc = str(format(float(itself) / float(allocate) * 100, '.2f'))
    # 本身占用/实例最大占用
    self_ins = str(format(float(itself) / float(instance) * 100, '.2f'))

    # 组合数据
    merge = self_alloc + "%/" + self_ins + "%-" + str(itself) + signal + "/" + str(allocate) + signal + "/" + \
        str(instance) + signal
    return merge


def instance_insert_mysql(ip, user, instance, account_name):

    # 定时任务获取的文件名
    filename = '/home/time_task/merge_info_' + ip + '.txt'
    # 根据ip地址读取time_task文件夹下的相应文件
    with open(filename, 'r') as f:
        info = f.readlines()
    for data in info:
        it_server = data.split(' ')
        server_name = it_server[0]

        # 如果该服务器flag状态标志为0，则continue,不插入数据。
        flag = ServerPid.objects.get(server_name=server_name).flag
        if flag == 0:
            continue
        server_port = it_server[1]
        # 最大人数取值出现错误，则用0代替，表示出错
        if it_server[2] == '':
            server_max_player = 0
        else:
            server_max_player = it_server[2]

        # 该服务器模式
        pattern = Version.objects.get(server_name=server_name).pattern

        # 该服务器模式的配置信息
        allocate = Pattern.objects.get(pattern=pattern)
        # 该服务器所在实例的实例雷ixng
        instance_max = InsType.objects.get(ip=ip).ins_type
        # 利用正则表达式将实例最大配置的数字取出来
        instance_max = re.findall(r"\d+\.?\d*", instance_max)
        # pid = int(it_server[3])
        if it_server[4] == '' or len(it_server[4]) > 4:
            # 没有拿到在线人数，可能服务器未完全开启或连接超时。
            online = 0
        else:
            online = int(it_server[4])
        cpu = it_server[5]
        # 分配占用,int
        cpu_allocate = allocate.cpu_num

        # 实例最大占用,str
        cpu_instance = instance_max[0]

        # cpu组合数据
        # print(type(cpu),type(cpu_allocate),type(cpu_instance))
        cpu_merge = data_merge(format(float(cpu) * int(cpu_instance) / 100, ".2f"), cpu_allocate, cpu_instance, '')
        memory = it_server[6]
        # 分配内存,int
        mem_allocate = allocate.memory_num

        # 实例最大占用,str
        mem_instance = instance_max[1]

        # 内存组合数据
        mem_merge = data_merge(format(float(memory) * int(mem_instance) / 100, ".2f"), mem_allocate, mem_instance, 'G')

        # 发送流量占用
        send_flow = it_server[7]
        # 接收流量占用
        recv_flow = it_server[8]

        # 分配占用
        flow_allocate = allocate.flow_num
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

        # 该服务器的版本模式等信息
        server_info = Version.objects.get(server_name=server_name)
        # 该服务器所在平台
        plat = AddVersion.objects.get(version=server_info.version).plat
        # 向数据库插入此时状态信息
        server_list = ServerList(server_name=server_name, max_player=str(online) + '/' + server_max_player,
                                 cpu=cpu_merge, memory=mem_merge, send_flow=send_flow_merge, recv_flow=recv_flow_merge,
                                 version=server_info.version, pattern=server_info.pattern, zone=server_info.zone,
                                 plat=plat, run_company=server_info.run_company, ip=ip, user=user, port=server_port,
                                 time=datetime.datetime.now(), account=account_name, instance_id=instance,
                                 is_activate=1, server_rule_id=1)
        server_list.save(force_insert=True)

        # 该服务器名称在server_name_rule中id
        server_id = ServerNameRule.objects.get(server_name=server_name).id
        # 数据存储在缓存中。
        redis_conn = get_redis_connection('default')
        redis_conn.hmset('server:%d' % server_id,
                         {'server_name': server_name, 'max_player': str(online) + '/' + server_max_player,
                          'cpu': cpu_merge, 'memory': mem_merge, 'send_flow': send_flow_merge,
                          'recv_flow': recv_flow_merge, 'version': server_info.version, 'pattern': server_info.pattern,
                          'zone': server_info.zone, 'plat': plat, 'run_company': server_info.run_company, 'ip': ip,
                          'user': user, 'port': server_port, 'account': account_name, 'instance_id': instance,
                          'is_activate': 1, 'server_rule_id': server_id})


@shared_task
def server_status():
    # 休眠5秒，等待所有服务器信息全部传过来
    time.sleep(5)
    data = Account.objects.values_list('account_name', 'account_id', 'account_key')
    for info in data:
        try:
            # 密钥
            cred = credential.Credential(info[1], info[2])
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cvm.tencentcloudapi.com"

            # 服务器所在大区
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = cvm_client.CvmClient(cred, "ap-beijing", clientProfile)

            # 向腾讯云发送实例列表描述请求
            req = models.DescribeInstancesRequest()
            params = '{}'
            req.from_json_string(params)

            # 腾讯云应当包
            resp = client.DescribeInstances(req)
            # 腾讯云应答包，json串,string
            # print(resp.to_json_string())

            # 转换为python字典
            res = json.loads(resp.to_json_string())

            # 该账户下总的实例个数
            total = res['TotalCount']
            # 一个账户下多个实例,根据内网ip进行通信，做好对等连接
            for i in range(total):
                pub_ip = res['InstanceSet'][0]['PublicIpAddresses']
                # PriIp = res['InstanceSet'][i]['PrivateIpAddresses']
                # print(PriIp)
                # 根据公网Ip获得一个实例上所有游戏服务器的名称,人数，繁忙服务器台数，空闲服务器台数
                instance_insert_mysql(''.join(pub_ip), 'root', res['InstanceSet'][0]['InstanceId'], info[0])
                # os.system("echo '%s' /home/tt.txt" % PriIp)
                # instance_insert_mysql(''.join(PriIp), 'root', res['InstanceSet'][i]['InstanceId'], info[1])

        except TencentCloudSDKException as err:
            print(err)


@shared_task
def monitor_process():
    # # 数据库连接
    conn = pymysql.connect('localhost', 'root', 'P@ssw0rd1', 'zero_server')
    # 创建游标对象
    cursor = conn.cursor()
    # 所有游戏服务器名称
    server_name_sql = "select server_name from zero_server_pid;"
    cursor.execute(server_name_sql)
    server_name = [x[0] for x in cursor.fetchall()]
    for file in os.listdir("/home/pid_server/"):
        with open("/home/pid_server/" + file, 'r') as f:
            data = f.readlines()
            ip = file.replace('.txt', '').split('_')[2]
            data_pid = [x.split(' ')[0] for x in data]
            # print(data_pid)
            data_server_name = [x.split(' ')[1].replace('\n', '') for x in data]
            for i in range(len(data_server_name)):
                if data_server_name[i] in server_name:
                    pid_sql = """select pid from zero_server_pid where server_name = '%s';""" % data_server_name[i]
                    cursor.execute(pid_sql)
                    cmd = "ls -ltr /home/log | grep %s | awk 'END {print}'" % (
                            data_server_name[i].replace('(', '_').replace(')', '') + '_')
                    latest_time = os.popen(cmd)
                    # 读取之后就消失,最新时间
                    time_temp = latest_time.read().split(' ')[-1].replace('\n', '').split('_')[3:5]
                    # 如果为空列表，则说明没有此服务器的崩溃信息。跳过
                    if not time_temp:
                        continue
                    point_time = time_temp[0] + ' ' + time_temp[1].replace('.log', '')
                    ss = datetime.datetime.strptime(point_time, "%Y-%m-%d %H:%M:%S")
                    print((datetime.datetime.now() - ss).seconds)
                    # 近一分钟内出现过崩溃日志，则记录在数据库中。(80秒，当日志时间为01秒传到管理服务器的，但是定时任务可能02秒。缓冲时间)
                    if (datetime.datetime.now() - ss).seconds <= 80:
                        # 在log文件夹下，找出该服务器的最新崩溃日志时间
                        cmd = "ls -ltr /home/log | grep %s | awk 'END {print}'" % \
                              data_server_name[i].replace('(', '_').replace(')', '') + '_'
                        latest_time = os.popen(cmd)
                        # 读取之后就消失,最新时间
                        time_temp = latest_time.read().split(' ')[-1].replace('\n', '').split('_')[3:5]
                        print(time_temp)
                        point_time = time_temp[0] + ' ' + time_temp[1].replace('.log', '')
                        # 在break_status文件下查找如果没有该时间，则将zero_server_list_update表的数据插入，time改为崩溃日志的时间
                        # 该进程已经死亡，则将之前数据插入到zero_break_log_search表中，
                        sql_select = """select server_name,max_player,cpu,memory,send_flow,recv_flow,version,zone,plat,
                                       run_company,ip,user from zero_server_list_update where server_name='%s';""" \
                                     % data_server_name[i]
                        cursor.execute(sql_select)
                        temp_data = cursor.fetchone()
                        sql_update = """insert into zero_break_log_search(server_name,max_player,cpu,memory,send_flow,
                                       recv_flow,version,zone,plat,run_company,ip,user,time) values('%s','%s','%s','%s',
                                       '%s','%s','%s','%s','%s','%s','%s','%s','%s')""" \
                                     % (temp_data[0], temp_data[1], temp_data[2], temp_data[3], temp_data[4],
                                        temp_data[5], temp_data[6], temp_data[7], temp_data[8], temp_data[9],
                                        temp_data[10], temp_data[11], point_time)
                        cursor.execute(sql_update)
                        sql = """update zero_server_pid set pid=%s where server_name='%s';""" \
                              % (data_pid[i], data_server_name[i])
                        cursor.execute(sql)
                        conn.commit()
                # 误删操作
                else:
                    # 如果zero_server_list_update中有该服务器名名称，则是误删，否则是更新服务器。
                    search_sql = "select count(*) from zero_server_list_update where server_name='%s';" % \
                                 data_server_name[i]
                    cursor.execute(search_sql)
                    if cursor.fetchone()[0] != 0:
                        sql = """insert into zero_server_pid(server_name,pid,ip,user,flag)
                                       values('%s','%s','%s','%s',1)""" % (data_server_name[i], data_pid[0], ip, 'root')

                        cursor.execute(sql)
                        conn.commit()
    # 关闭数据库连接和ssh连接
    cursor.close()
    conn.close()
