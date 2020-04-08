from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models


def buy(secu_id, secu_key, region, pay_type, zone, instype,imageid,disksize,width):
    try:
        cred = credential.Credential(secu_id, secu_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cvm.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cvm_client.CvmClient(cred, region, clientProfile)

        req = models.RunInstancesRequest()
        params = '{"InstanceChargeType":"%s","Placement":{"Zone":"%s"},' \
                 '"InstanceType":"%s","ImageId":"%s","SystemDisk":{"DiskSize":%d},' \
                 '"InternetAccessible":{"InternetMaxBandwidthOut":%d,"PublicIpAssigned":true}}' \
                 % (pay_type, zone, instype, imageid, int(disksize), int(width))
        req.from_json_string(params)

        resp = client.RunInstances(req)
        # print(resp.to_json_string())
        return "购买成功，等待实例创建开启"

    except TencentCloudSDKException as err:
        print(err)


if __name__ == "__main__":
    buy(secu_id="AKIDjEUUGoJKCxvhCReDk1EBrGPWfZDbqgNo", secu_key="LRJwJn6AzYqse9T8YicGgqkTs473kIag",
        region="ap-beijing", pay_type="POSTPAID_BY_HOUR", zone="ap-beijing-1", instype="S1.MEDIUM4",
        imageid="img-9qabwvbn", disksize=50, width=5)
