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

from cloud_user.models import Account
from server_list import real_time_region
from server_list.models import InsType


def ip(ins_type):

    # 查询所有账户
    all_info = Account.objects.all().values_list('account_name', 'account_id', 'account_key')
    # 查询实例表中所有ip,放在ip_info列表中
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

                    # 组合cpu/memory/disk_size/internet_width信息
                    merge = str(ins_cpu) + '核/' + str(ins_memory) + 'G/' + str(internet_width) + 'Mbps/' +\
                        str(disk_size) + 'G'

                    # 插入数据库, 部署后改为内网
                    # str_ip = str(ins_set['PublicIpAddresses']).replace('[', '').replace(']', '').replace("'", "")
                    str_ip = str(ins_set['PublicIpAddresses']).replace('[', '').replace(']', '').replace("'", "")
                    # 如果要开设的服务器的实例类型和该实例一样，则加入可开设服务器的ip列表
                    if ins_type == merge:
                        available_ip.append(str_ip)
                    # 查看ip是否已经存在，不存在则插入，存在则更新
                    ins_type_save = InsType(ins_type=merge, ip=str_ip, account_name=info[0])
                    ins_type_save.save()

        except TencentCloudSDKException as err:
            print(err)
            raise err

    return available_ip


if __name__ == "__main__":
    ip(ins_type='')
