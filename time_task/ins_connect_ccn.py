#！/root/.virtualenvs/server/bin/python3
# -*- coding:utf-8 -*-
# @Time: 4/15/20 6:45 PM
# @Author:bayhax
# @Filename: ins_connect_ccn.py
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.vpc.v20170312 import vpc_client, models


def connect():
    try:
        cred = credential.Credential("AKIDYxBJFzqxBDNODqfcjgR2TkpiQvGOiBpI", "Pf0EHzYxAC6nKfqskSzObdUCk9MOGxUp")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "vpc.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = vpc_client.VpcClient(cred, "ap-beijing", clientProfile)

        req = models.AttachCcnInstancesRequest()
        params = '{"CcnId":"ccn-ofx5eisr","Instances":[{"InstanceType":"VPC", "InstanceId":"vpc-3p3hrzeq", ' \
                 '"InstanceRegion":"ap-beijing"}]}'
        req.from_json_string(params)

        resp = client.AttachCcnInstances(req)
        print(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)


if __name__ == "__main__":
    connect()