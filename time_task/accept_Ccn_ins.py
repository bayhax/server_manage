#！/root/.virtualenvs/server/bin/python3
# -*- coding:utf-8 -*-
# @Time: 4/15/20 7:37 PM
# @Author:bayhax
# @Filename: accept_Ccn_ins.py
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.vpc.v20170312 import vpc_client, models


def accept():
    try:
        cred = credential.Credential("AKIDYxBJFzqxBDNODqfcjgR2TkpiQvGOiBpI", "Pf0EHzYxAC6nKfqskSzObdUCk9MOGxUp")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "vpc.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = vpc_client.VpcClient(cred, "ap-beijing", clientProfile)

        req = models.AcceptAttachCcnInstancesRequest()
        params = '{"CcnId":"ccn-394zj0pv","Instances":[{"InstanceId":"ins-n56dbxj9","InstanceRegion":"ap-beijing"}]}'
        req.from_json_string(params)

        resp = client.AcceptAttachCcnInstances(req)
        print(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)


if __name__ == "__main__":
    accept()