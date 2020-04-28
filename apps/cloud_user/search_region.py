#!/root/.virtualenvs/server/bin/python3
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models
import json

from server_list.models import InsType


def insert_ins_type(account_name, httpProfile, cred, region):

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

        internet_width = res['InternetBandwidthConfigSet'][0]['InternetAccessible']['InternetMaxBandwidthOut']

        # 组合cpu/memory/disksize/bandwidth信息
        merge = str(ins_cpu) + '核/' + str(ins_memory) + 'G/' + str(internet_width) + 'Mbps/' + str(disk_size) + 'G'

        # 插入数据库,上线部署后换为私有ip
        str_ip = str(ins_set['PublicIpAddresses']).replace('[', '').replace(']', '').replace("'", "")
        # str_ip = str(ins_set['PrivateIpAddresses']).replace('[', '').replace(']', '').replace("'", "")

        # 查看ip是否已经存在，不存在则插入，存在则更新
        ins_type = InsType(ins_type=merge, ip=str_ip, account_name=account_name)
        ins_type.save()


def search(account_name, secu_id, secu_key):
    region_name = []
    region = []
    try:
        # key,id
        cred = credential.Credential(secu_id, secu_key)
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
            insert_ins_type(account_name, httpProfile, cred, res['RegionSet'][i]['Region'])
            region_name.append(res['RegionSet'][i]['RegionName'])

    except TencentCloudSDKException as err:
        print(err)

    return region, region_name


if __name__ == "__main__":
    # search(secu_id='AKIDjEUUGoJKCxvhCReDk1EBrGPWfZDbqgNo',secu_key="LRJwJn6AzYqse9T8YicGgqkTs473kIag")
    search(account_name='', secu_id='AKIDYxBJFzqxBDNODqfcjgR2TkpiQvGOiBpI', secu_key="Pf0EHzYxAC6nKfqskSzObdUCk9MOGxUp")
