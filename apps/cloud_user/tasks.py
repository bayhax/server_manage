# ！/root/.virtualenvs/server/bin/python3
# -*- coding:utf-8 -*-
# @Time: 4/22/20 3:14 PM
# @Author:bayhax
# @Filename: tasks.py
from __future__ import absolute_import
from celery import shared_task
# from server_manage.celery import app
from cloud_user.models import Account, ZoneCode, AccountZone

import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models
import pymysql


@shared_task
def insert_ins_type():
    # 连接数据库，创建游标
    conn = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    cursor = conn.cursor()
    # sql查询语句执行,查询所有账户
    sql = "select account_name,account_id,account_key from zero_cloud_user;"
    cursor.execute(sql)
    # 查询结果
    all_info = cursor.fetchall()

    # 查询实例表中所有ip,放在ip_info列表中
    sql2 = "select ip from zero_ins_type;"
    cursor.execute(sql2)
    ip_data = cursor.fetchall()
    ip_info = []
    for i in ip_data:
        ip_info.append(i[0])

    # 遍历账户查询结果
    for info in all_info:
        try:
            # 根据账户名称查询区域region
            sql_region = "select region from zero_account_zone where account_name='%s';" % info[0]
            cursor.execute(sql_region)
            region_name = cursor.fetchone()
            # 将region_name这个大字符串变成列表,并去掉字符串中的空格
            region_name = [x.strip() for x in region_name[0].split(',')]
            # 密钥
            cred = credential.Credential(info[1], info[2])
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cvm.tencentcloudapi.com"

            # 服务器所在大区
            for region in region_name:
                # 根据region中文名在zero_zone_code表中查询中对应代号,code[0](code是数据库查询返回的元组)
                sql_code = "select code from zero_zone_code where zone='%s';" % region
                cursor.execute(sql_code)
                code = cursor.fetchone()

                clientProfile = ClientProfile()
                clientProfile.httpProfile = httpProfile
                client = cvm_client.CvmClient(cred, code[0], clientProfile)

                # 向腾讯云发送实例列表描述请求
                req = models.DescribeInstancesRequest()
                params = '{}'
                req.from_json_string(params)

                # 腾讯云应当包
                resp = client.DescribeInstances(req)

                # 转换为python字典
                res = json.loads(resp.to_json_string())

                # 实例集合
                for ins_set in res['InstanceSet']:
                    ins_cpu = ins_set['CPU']
                    ins_memory = ins_set['Memory']
                    ins_id = ins_set['InstanceId']
                    disk_size = ins_set['SystemDisk']['DiskSize']

                    req = models.DescribeInstanceInternetBandwidthConfigsRequest()
                    params = '{"InstanceId":"%s"}' % ins_id
                    req.from_json_string(params)

                    # 查询实例带宽配置
                    resp = client.DescribeInstanceInternetBandwidthConfigs(req)
                    # 转成python字典
                    res = json.loads(resp.to_json_string())

                    internet_width = res['InternetBandwidthConfigSet'][0]['InternetAccessible'][
                        'InternetMaxBandwidthOut']

                    # 组合cpu/memory/disksize/bandwidth信息
                    merge = str(ins_cpu) + '核/' + str(ins_memory) + 'G/' \
                        + str(disk_size) + 'G/' + str(internet_width) + 'Mbps'

                    # 插入数据库
                    str_ip = str(ins_set['PrivateIpAddressed']).replace('[', '').replace(']', '').replace("'", "")

                    # 查看ip是否已经存在，不存在则插入，存在则更新
                    if str_ip not in ip_info:
                        insert_sql = "insert into zero_ins_type(ins_type,ip,account_name) values('%s','%s','%s')" \
                                     % (merge, str_ip, info[0])
                        cursor.execute(insert_sql)
                    else:
                        update_sql = "update zero_ins_type set ins_type='%s' where ip='%s';" % (merge, str_ip)
                        cursor.execute(update_sql)
                    conn.commit()

        except TencentCloudSDKException as err:
            print(err)
            raise err

    # 关闭数据库和游标
    cursor.close()
    conn.close()


def search_zone(security_id, security_key, region):
    # 可用区代号，中文名
    zone = []
    zone_name = []
    try:
        # id,key
        cred = credential.Credential(security_id, security_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cvm.tencentcloudapi.com"

        # 要查询的区域
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cvm_client.CvmClient(cred, region, clientProfile)

        # 返回结果可用区信息
        req = models.DescribeZonesRequest()
        params = '{}'
        req.from_json_string(params)

        # 结果转成字典
        resp = client.DescribeZones(req)
        # print(resp.to_json_string())
        res = json.loads(resp.to_json_string())

        # 返回可用区的中文名和代号

        for i in range(res['TotalCount']):
            zone.append(res['ZoneSet'][i]['Zone'])
            zone_name.append(res['ZoneSet'][i]['ZoneName'])

    except TencentCloudSDKException as err:
        print(err)

    return zone, zone_name


def search_region(security_id, security_key):
    region_name = []
    region = []
    try:
        # key,id
        cred = credential.Credential(security_id, security_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cvm.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cvm_client.CvmClient(cred, "", clientProfile)

        # 所有可用地域
        req = models.DescribeRegionsRequest()
        params = '{}'
        req.from_json_string(params)

        # 结果转成字典类型
        resp = client.DescribeRegions(req)
        # print(resp.to_json_string())
        res = json.loads(resp.to_json_string())

        for i in range(res['TotalCount']):
            region.append(res['RegionSet'][i]['Region'])
            region_name.append(res['RegionSet'][i]['RegionName'])

    except TencentCloudSDKException as err:
        print(err)

    return region, region_name


@shared_task
def insert_account_zone():
    # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    # db = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # # 使用 cursor() 方法创建一个游标对象 cursor
    # cursor = db.cursor()
    #
    # sql = """select account_name,account_id,account_key from zero_cloud_user;"""
    #
    # # 查询所有账户
    # cursor.execute(sql)
    # account_info = cursor.fetchall()
    account_info = Account.objects.values_list('account_name', 'account_id', flat=True)

    # 遍历账户更新可用区
    for acc in account_info:
        # 总区域
        region, region_name = search_region(acc[1], acc[2])
        # 将区域插入进数据表
        for i in range(len(region)):
            # search_sql = """select count(*) from zero_zone_code where zone='%s';""" % region_name[i]
            # cursor.execute(search_sql)
            # count = cursor.fetchone()
            # count = ZoneCode.objects.filter(zone=region_name[i]).count()
            # 如果没有该名称，则插入，否则更新
            zone_code = ZoneCode(zone=region_name[i], code=region[i])
            zone_code.save()
            # if count == 0:
            #     insert_sql = "insert into zero_zone_code(code,zone) values('%s','%s');" % (region[i], region_name[i])
            #     cursor.execute(insert_sql)
            # else:
            #     update_sql = """update zero_zone_code set code='%s' where zone='%s';""" % (region[i], region_name[i])
            #     cursor.execute(update_sql)
            # db.commit()

        # 该区域的可用区
        for reg in region:
            zone_code, zone_name = search_zone(acc[1], acc[2], reg)
            merge = dict(zip(zone_code, zone_name))
            # 查询zero_zone_code表中是否有该区域
            for key, value in merge.items():
                # search_sql = """select count(*) from zero_zone_code where zone='%s';""" % value
                # cursor.execute(search_sql)
                # count = cursor.fetchone()
                zone_code = ZoneCode(zone=value, code=key)
                zone_code.save()
                # # 如果没有该名称，则插入，否则更新
                # if count[0] == 0:
                #     insert_sql = """insert into zero_zone_code(code,zone) values('%s','%s');""" % (key, value)
                #     cursor.execute(insert_sql)
                # else:
                #     update_sql = """update zero_zone_code set code='%s' where zone='%s';""" % (key, value)
                #     cursor.execute(update_sql)
                # db.commit()

        # 获取所有可用区，将可用区变成字符串存到数据库中
        all_zone = str(region_name).replace("'", "").replace('[', '').replace(']', '')
        # search_sql = """select count(*) from zero_account_zone where account_name='%s';""" % acc[0]
        # cursor.execute(search_sql)
        # count2 = cursor.fetchone()
        account_zone = AccountZone(account_name=acc[0], account_id=acc[1], account_key=acc[2], region=all_zone)
        account_zone.save()
        # 如果没有该账户，则插入，否则更新
        # if count2[0] == 0:
        #     insert_sql2 = """insert into zero_account_zone(account_name,account_id,account_key,region)
        #                         values('%s','%s','%s','%s');""" % (acc[0], acc[1], acc[2], all_available_zone)
        #     cursor.execute(insert_sql2)
        # else:
        #     update_sql2 = """update zero_account_zone set region='%s' where account_name='%s';""" \
        #                   % (all_available_zone, acc[0])
        #     cursor.execute(update_sql2)
        # db.commit()

    # cursor.close()
    # # 关闭数据库连接
    # db.close()
