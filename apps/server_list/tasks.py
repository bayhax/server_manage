# ！/root/.virtualenvs/server/bin/python3
# -*- coding:utf-8 -*-
# @Time: 4/22/20 3:16 PM
# @Author:bayhax
# @Filename: tasks.py
from __future__ import absolute_import

import pytz
from celery import shared_task

import datetime
import json
import os
import time

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.cvm.v20170312 import cvm_client, models

from cloud_user.models import Account, ServerAccountZone, ZoneCode
from config.models import Version, AddVersion
from log.models import BreakLogSearch
from server_list.models import ServerNameRule, ServerPid, ServerList, ServerListUpdate
from django_redis import get_redis_connection


def instance_insert_mysql(ip, user, instance, account_name):
    # zero_server_name_rule表中所有服务器名称
    server_list_update_server = ServerListUpdate.objects.all().values_list('server_name', flat=True)
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

        if it_server[4] == '' or len(it_server[4]) > 4:
            # 没有拿到在线人数，可能服务器未完全开启或连接超时。
            online = 0
        else:
            online = int(it_server[4])
        cpu = it_server[5]

        memory = it_server[6]
        # 发送流量占用
        send_flow = it_server[7]
        # 接收流量占用,最后数据，去除空格
        recv_flow = it_server[8].strip()

        # 该服务器的版本模式等信息
        server_info = Version.objects.get(server_name=server_name)
        # 该服务器所在平台
        plat = AddVersion.objects.get(version=server_info.version).plat
        # 存到数据库中，
        time_point = datetime.datetime.now(pytz.timezone('Asia/Shanghai')) + datetime.timedelta(hours=8)
        # print(time_point)
        server_rule_id = ServerNameRule.objects.get(server_name=server_name).id
        # 向数据库插入此时状态信息
        server_list = ServerList(server_name=server_name, max_player=str(online) + '/' + server_max_player,
                                 cpu=cpu, memory=memory, send_flow=send_flow, recv_flow=recv_flow,
                                 version=server_info.version, pattern=server_info.pattern, zone=server_info.zone,
                                 plat=plat, run_company=server_info.run_company, ip=ip, user=user, port=server_port,
                                 time=time_point, account=account_name, instance_id=instance,
                                 is_activate=1, server_rule_id=server_rule_id)
        server_list.save(force_insert=True)
        # 存在则更新
        if server_name in server_list_update_server:
            ServerListUpdate.objects.filter(server_name=server_name).update(
                max_player=str(online) + '/' + server_max_player,
                cpu=cpu, memory=memory, send_flow=send_flow, recv_flow=recv_flow,
                version=server_info.version, pattern=server_info.pattern, zone=server_info.zone,
                plat=plat, run_company=server_info.run_company, ip=ip, user=user, port=server_port,
                time=time_point, account=account_name, instance_id=instance)
        # 不存在则插入
        else:
            server_list_update = ServerListUpdate(server_name=server_name,
                                                  max_player=str(online) + '/' + server_max_player,
                                                  cpu=cpu, memory=memory, send_flow=send_flow, recv_flow=recv_flow,
                                                  version=server_info.version, pattern=server_info.pattern,
                                                  zone=server_info.zone,
                                                  plat=plat, run_company=server_info.run_company, ip=ip, user=user,
                                                  port=server_port,
                                                  time=time_point, account=account_name,
                                                  instance_id=instance,
                                                  is_activate=1, server_rule_id=server_rule_id)
            server_list_update.save(force_insert=True)
        # 该服务器名称在server_name_rule中id
        server_id = ServerNameRule.objects.get(server_name=server_name).id
        # 数据存储在缓存中。
        redis_conn = get_redis_connection('default')
        redis_conn.hmset('server:%d' % server_id,
                         {'server_name': server_name, 'max_player': str(online) + '/' + server_max_player,
                          'cpu': cpu, 'memory': memory, 'send_flow': send_flow, 'recv_flow': recv_flow,
                          'version': server_info.version, 'pattern': server_info.pattern,
                          'zone': server_info.zone, 'plat': plat, 'run_company': server_info.run_company, 'ip': ip,
                          'user': user, 'port': server_port, 'account': account_name,
                          'instance_id': instance, 'is_activate': 1, 'server_rule_id': server_id})


@shared_task
def server_status():
    # 休眠5秒，等待所有服务器信息全部传过来
    time.sleep(5)
    region = []
    data = Account.objects.values_list('account_name', 'account_id', 'account_key')
    for info in data:
        try:
            # 密钥
            cred = credential.Credential(info[1], info[2])
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cvm.tencentcloudapi.com"

            # clientProfile = ClientProfile()
            # clientProfile.httpProfile = httpProfile
            # client = cvm_client.CvmClient(cred, "", clientProfile)
            #
            # # 所有可用地域，
            # req = models.DescribeRegionsRequest()
            # params = '{}'
            # req.from_json_string(params)
            #
            # # 结果转成字典类型
            # resp = client.DescribeRegions(req)
            # # print(resp.to_json_string())
            # res = json.loads(resp.to_json_string())
            #
            # for i in range(res['TotalCount']):
            #     region.append(res['RegionSet'][i]['Region'])
            # 账户已经配置（可能购买过服务器）的地区
            region_name = ServerAccountZone.objects.filter(account_name=info[0]).values_list('zone', flat=True)
            for r_name in region_name:
                region.append(ZoneCode.objects.get(zone=r_name).code)
            for reg in region:
                # 服务器所在大区
                clientProfile = ClientProfile()
                clientProfile.httpProfile = httpProfile
                client = cvm_client.CvmClient(cred, reg, clientProfile)

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
                    pub_ip = res['InstanceSet'][i]['PrivateIpAddresses']
                    # PriIp = res['InstanceSet'][i]['PrivateIpAddresses']
                    # print(PriIp)
                    # 根据公网Ip获得一个实例上所有游戏服务器的名称,人数，繁忙服务器台数，空闲服务器台数
                    instance_insert_mysql(''.join(pub_ip), 'root', res['InstanceSet'][i]['InstanceId'], info[0])
                    # os.system("echo '%s' /home/tt.txt" % PriIp)
                    # instance_insert_mysql(''.join(PriIp), 'root', res['InstanceSet'][i]['InstanceId'], info[1])

        except TencentCloudSDKException as err:
            print(err)


@shared_task
def monitor_process():
    # 连接redis
    redis_conn = get_redis_connection('default')
    # 获取所有服务器名称
    server_name = ServerNameRule.objects.all().values_list('server_name', flat=True)
    for file in os.listdir("/home/pid_server/"):
        with open("/home/pid_server/" + file, 'r') as f:
            data = f.readlines()
            ip = file.replace('.txt', '').split('_')[2]
            data_pid = [x.split(' ')[0] for x in data]
            # print(data_pid)
            data_server_name = [x.split(' ')[1].replace('\n', '') for x in data]
            for i in range(len(data_server_name)):
                if data_server_name[i] in server_name:

                    cmd = "ls -ltr /home/log | grep %s | grep -v %s | awk 'END {print}'" % (
                            data_server_name[i].replace('(', '_').replace(')', '') + '_', data_server_name[i].replace('(', '_').replace(')', '') + '_' + 'update')
                    latest_time = os.popen(cmd)
                    # 读取之后就消失,最新时间
                    time_temp = latest_time.read().split(' ')[-1].replace('\n', '').split('_')[3:5]
                    # 如果为空列表，则说明没有此服务器的崩溃信息。跳过
                    if not time_temp:
                        continue
                    point_time = time_temp[0] + ' ' + time_temp[1].replace('.log', '')
                    ss = datetime.datetime.strptime(point_time, "%Y-%m-%d %H:%M:%S")

                    # 近一分钟内出现过崩溃日志，则记录在数据库中。(80秒，当日志时间为01秒传到管理服务器的，但是定时任务可能02秒。缓冲时间)
                    if (datetime.datetime.now() - ss).total_seconds() <= 80:
                        # 在log文件夹下，找出该服务器的最新崩溃日志时间
                        cmd = "ls -ltr /home/log | grep %s | awk 'END {print}'" % \
                              data_server_name[i].replace('(', '_').replace(')', '') + '_'
                        latest_time = os.popen(cmd)
                        # 读取之后就消失,最新时间
                        time_temp = latest_time.read().split(' ')[-1].replace('\n', '').split('_')[3:5]
                        # print(time_temp)
                        point_time = time_temp[0] + ' ' + time_temp[1].replace('.log', '')
                        # 加八小时存入数据库,（数据库中是utc时间），加八小时是为了成北京时间，以后查询方便。
                        point_time = datetime.datetime.strptime(point_time, "%Y-%m-%d %H:%M:%S") + \
                            datetime.timedelta(hours=8)

                        server_rule_id = ServerNameRule.objects.get(server_name=data_server_name[i]).id

                        temp_data = redis_conn.hmget('server:%d' % server_rule_id, 'server_name', 'max_player', 'cpu',
                                                     'memory', 'send_flow', 'recv_flow', 'version', 'zone', 'plat',
                                                     'run_company', 'ip', 'user')
                        temp_data = [x.decode('utf-8') for x in temp_data]

                        break_log_search = BreakLogSearch(server_name=temp_data[0], max_player=temp_data[1],
                                                          cpu=temp_data[2], memory=temp_data[3], send_flow=temp_data[4],
                                                          recv_flow=temp_data[5], version=temp_data[6],
                                                          zone=temp_data[7], plat=temp_data[8],
                                                          run_company=temp_data[9], ip=temp_data[10],
                                                          user=temp_data[11],
                                                          time=point_time, server_rule_id=server_rule_id)
                        break_log_search.save()

                        ServerPid.objects.filter(server_name=data_server_name[i]).update(pid=data_pid[i])

                # 误删操作
                else:
                    # 如果zero_server_list_update中有该服务器名名称，则是误删，否则是更新服务器。
                    res = ServerListUpdate.objects.filter(server_name=data_server_name[i])
                    if res.exists():
                        server_rule_id = ServerListUpdate.objects.get(server_name=data_server_name[i]).server_rule_id
                        exists = redis_conn.exists('server:%d' % server_rule_id)
                        if exists != 0:
                            server_pid = ServerPid(server_name=data_server_name[i], pid=data_pid[0], ip=ip,
                                                   user='root', flag=1)
                            server_pid.save(force_insert=True)
