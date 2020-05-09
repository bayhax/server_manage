#!/root/.virtualenvs/server/bin/python3
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.vpc.v20170312 import vpc_client, models
import json


# 在管理服务器创建云联网
def create(region, ccn_name, ccn_description, instance_charge_type, band_width_limit_type):
    """管理服务器创建云联网，目前只为北京地域，后续要有各地域，在管理服务器应该购买各地域的实例，用于通信传送服务器文件等"""

    try:
        cred = credential.Credential("AKIDYxBJFzqxBDNODqfcjgR2TkpiQvGOiBpI", "Pf0EHzYxAC6nKfqskSzObdUCk9MOGxUp")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "vpc.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = vpc_client.VpcClient(cred, region, clientProfile)

        req = models.CreateCcnRequest()
        params = '{"CcnName":"%s","CcnDescription":"%s","InstanceChargeType":"%s","BandwidthLimitType":"%s"}' \
                 % (ccn_name, ccn_description, instance_charge_type, band_width_limit_type)
        req.from_json_string(params)

        resp = client.CreateCcn(req)
        print(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)

    # 获取Ccn列表。
    # 获取管理服务器相关地域的CcnId,管理服务器创建后不会轻易改变的（如 北京  ccn-394zj0pv）
    # 获取要关联管理服务器云联网的实例id，主账号（管理服务器），大区，要关联管理服务器云联网

    # 管理服务器云联网接受关联实例


if __name__ == "__main__":
    create(region='ap-beijing', ccn_name='BeijingCcn', ccn_description='北京地域云联网', instance_charge_type='PREPAID',
           band_width_limit_type='INTER_REGION_LIMIT')
