import json

import pymysql
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models


def search(secu_id, secu_key, region, cpu, memory):
    try:
        # 连接数据库获取区域代码
        conn = pymysql.connect('localhost', 'root', 'P@ssw0rd1', 'zero_server')
        cursor = conn.cursor()
        sql = "select code from zero_zone_code where zone='%s';" % region
        cursor.execute(sql)
        region_data = cursor.fetchone()

        cred = credential.Credential(secu_id, secu_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cvm.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cvm_client.CvmClient(cred, region_data[0], clientProfile)

        req = models.DescribeInstanceTypeConfigsRequest()
        # 过滤实例机型，S1，M1等
        params = '{}'
        req.from_json_string(params)

        # 腾讯云返回结果
        resp = client.DescribeInstanceTypeConfigs(req)

        # json转字典
        instance_type_set = json.loads(resp.to_json_string())
        # 查询出满足cpu,memory配置的机型地区zone,实例类型名称放入列表中，防止重复的无法放入
        zone = []
        ins_type = []
        for ins in instance_type_set['InstanceTypeConfigSet']:
            if ins['CPU'] == int(cpu) and ins['Memory'] == int(memory):
                zone.append(ins['Zone'])
                ins_type.append(ins['InstanceType'])
        # 返回地区和类型，一一对应
        return zone, ins_type

    except TencentCloudSDKException as err:
        print(err)


if __name__ == "__main__":
    search(secu_id="AKIDjEUUGoJKCxvhCReDk1EBrGPWfZDbqgNo", secu_key="LRJwJn6AzYqse9T8YicGgqkTs473kIag",
           region="ap-guangzhou", cpu=2, memory=4)
