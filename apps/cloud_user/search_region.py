#!/root/.virtualenvs/server/bin/python3
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models
import json


def search(secu_id, secu_key):
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
            region_name.append(res['RegionSet'][i]['RegionName'])

    except TencentCloudSDKException as err:
        print(err)

    return region, region_name


if __name__ == "__main__":
    # search(secu_id='AKIDjEUUGoJKCxvhCReDk1EBrGPWfZDbqgNo',secu_key="LRJwJn6AzYqse9T8YicGgqkTs473kIag")
    search(secu_id='AKIDYxBJFzqxBDNODqfcjgR2TkpiQvGOiBpI', secu_key="Pf0EHzYxAC6nKfqskSzObdUCk9MOGxUp")
