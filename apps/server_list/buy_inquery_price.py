import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models

from cloud_user.models import ZoneCode
from config.models import Pattern


def inquery(secu_id, secu_key, pattern, region, zone, instype):
    try:
        data = Pattern.objects.get(pattern=pattern)
        disksize = int((data.ins_type).split('/')[3].replace('G', ''))
        pay_type = data.pay_type

        # 根据region获取区域代码
        region = ZoneCode.objects.get(zone=region).code
        # 连接腾讯云
        cred = credential.Credential(secu_id, secu_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cvm.tencentcloudapi.com"

        # 设定区域
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cvm_client.CvmClient(cred, region, clientProfile)

        # 获取镜像ID
        req_imageid = models.DescribeImagesRequest()
        params = '{}'
        req_imageid.from_json_string(params)

        resp_imageid = client.DescribeImages(req_imageid)
        # 转成字典获取第一个镜像id
        imageid_set = json.loads(resp_imageid.to_json_string())
        imageid = imageid_set['ImageSet'][0]['ImageId']

        # 获取单位价格,根据付费模式，参数不同。包年报月/按小时后付费
        req = models.InquiryPriceRunInstancesRequest()
        if pay_type == "PREPAID":
            params = '{"InstanceChargeType":"%s", "InstanceChargePrepaid":{"Period":3}, "Placement":{"Zone":"%s"},' \
                     '"InstanceType":"%s","ImageId":"%s","SystemDisk":{"DiskSize":%d}}' \
                     % (pay_type, zone, instype, imageid, disksize)
        else:
            params = '{"InstanceChargeType":"%s", "Placement":{"Zone":"%s"},' \
                     '"InstanceType":"%s","ImageId":"%s","SystemDisk":{"DiskSize":%d}}' \
                     % (pay_type, zone, instype, imageid, disksize)
        req.from_json_string(params)

        resp = client.InquiryPriceRunInstances(req)
        # print(resp.to_json_string())
        # 转为python字典
        price_data = json.loads(resp.to_json_string())
        price = price_data['Price']['InstancePrice']['UnitPrice']

        return price, region, zone, instype, imageid, pay_type, disksize

    except TencentCloudSDKException as err:
        raise err


if __name__ == "__main__":
    inquery(secu_id="AKIDjEUUGoJKCxvhCReDk1EBrGPWfZDbqgNo", secu_key="LRJwJn6AzYqse9T8YicGgqkTs473kIag",
            pattern='test', region='华北地区(北京)', zone='ap-beijing-1', instype='S1.MEDIUM4')
