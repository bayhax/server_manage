#!/root/.virtualenvs/server/bin/python3
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models
import json


def search(secu_id, secu_key, region):
    # 可用区代号，中文名
    zone = []
    zone_name = []
    try:
        # id,key
        cred = credential.Credential(secu_id, secu_key)
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


if __name__ == "__main__":
    search(secu_id='AKIDJNHvM6lx0pMegcvwEG4cuwra3Gl2roKa', secu_key='B6lAj481e3HFwW2IIQDxWpruqXy88tOd',
           region='ap-beijing')
