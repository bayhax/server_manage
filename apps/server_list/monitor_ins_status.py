#!/root/.virtualenvs/server/bin/python3
import datetime
import json

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models


def monitor(secu_id, secu_key, region):
    # flag = 0
    ins_id = ''
    try:
        cred = credential.Credential(secu_id, secu_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cvm.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cvm_client.CvmClient(cred, region, clientProfile)

        # 查询实例列表
        req = models.DescribeInstancesRequest()
        params = '{}'
        req.from_json_string(params)

        resp = client.DescribeInstances(req)
        # 转成python字典
        ins_set = json.loads(resp.to_json_string())
        # 初始化比较时间
        temp = datetime.datetime.strptime("2000-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')

        # 遍历实例列表,取出创建时间比较拿到最新创建实例的那台实例id
        for ins in ins_set['InstanceSet']:
            create_time = datetime.datetime.strptime(ins['CreatedTime'].replace('T', ' ').replace('Z', ''),
                                                     '%Y-%m-%d %H:%M:%S')
            if temp < create_time:
                ins_id = ins['InstanceId']
        # 查看这台实例的状态,循环检测,直到状态为运行态停止
        while True:
            req = models.DescribeInstancesStatusRequest()
            params = '{"InstanceIds":["%s"]}' % ins_id
            req.from_json_string(params)

            resp = client.DescribeInstancesStatus(req)
            # 转成python字典
            status = json.loads(resp.to_json_string())
            if status['InstanceStatusSet'][0]['InstanceState'] == "RUNNING":
                flag = 1
                req_ip = models.DescribeInstancesRequest()
                params = '{"InstanceIds":["%s"]}' % ins_id
                req_ip.from_json_string(params)

                resp = client.DescribeInstances(req_ip)
                # 转成python字典
                ins_set = json.loads(resp.to_json_string())
                # ip = ins_set['InstanceSet'][0]['PrivateIpAddresses']
                ip = ins_set['InstanceSet'][0]['PrivateIpAddresses']
                break
        if flag == 1:
            return ip
        else:
            return 0

    except TencentCloudSDKException as err:
        print(err)


if __name__ == "__main__":
    monitor(secu_id='AKIDjEUUGoJKCxvhCReDk1EBrGPWfZDbqgNo', secu_key='LRJwJn6AzYqse9T8YicGgqkTs473kIag',
            region='ap-guangzhou')
