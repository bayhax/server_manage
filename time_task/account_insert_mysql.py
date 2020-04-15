#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import json
import time
import os
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models
import instance_insert_mysql
import pymysql


def insert():
    # 休眠10秒，等待所有服务器信息全部传过来
    time.sleep(10)
    # 连接数据库获取腾讯云账户信息
    conn = pymysql.connect('localhost', 'root', 'P@ssw0rd1', 'zero_server')
    cursor = conn.cursor()
    sql = "select * from zero_cloud_user;"
    cursor.execute(sql)
    data = cursor.fetchall()
    for info in data:
        try:
            # 密钥
            cred = credential.Credential(info[2], info[3])
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
                # pub_ip = res['InstanceSet'][0]['PrivateIpAddressed']
                PriIp = res['InstanceSet'][i]['PrivateIpAddresses']
                # print(PriIp)
                # 根据公网Ip获得一个实例上所有游戏服务器的名称,人数，繁忙服务器台数，空闲服务器台数
                # instance_insert_mysql.insert_mysql(''.join(pub_ip), 'root', res['InstanceSet'][0]['InstanceId'],
                #                                   info[1])
                # os.system("echo '%s' /home/tt.txt" % PriIp)
                instance_insert_mysql.insert_mysql(''.join(PriIp), 'root', res['InstanceSet'][i]['InstanceId'],
                                                   info[1])

        except TencentCloudSDKException as err:
            print(err)


if __name__ == "__main__":
    insert()
