#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models
import pymysql

from server_list import real_time_region


def ip(ins_type):
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

    # 返回可以新增服务器的ip
    available_ip = []
    # 遍历账户查询结果
    for info in all_info:
        try:
            # 密钥
            cred = credential.Credential(info[1], info[2])
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cvm.tencentcloudapi.com"
            region_code, region_name = real_time_region.search(info[1], info[2])
            # 服务器所在大区
            for region in region_code:

                clientProfile = ClientProfile()
                clientProfile.httpProfile = httpProfile
                client = cvm_client.CvmClient(cred, region, clientProfile)

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
                    merge = str(ins_cpu) + '核/' + str(ins_memory) + 'G/' + str(disk_size) + 'G/' \
                            + str(internet_width) + 'Mbps'

                    # 插入数据库
                    str_ip = str(ins_set['PrivateIpAddresses']).replace('[', '').replace(']', '').replace("'", "")
                    # 如果要开设的服务器的实例类型和该实例一样，则加入可开设服务器的ip列表
                    if ins_type == merge:
                        available_ip.append(str_ip)
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
    return available_ip


if __name__ == "__main__":
    ip(ins_type='')
