#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models
import pymysql


def insert():
    # 连接数据库，创建游标
    conn = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    cursor = conn.cursor()
    # sql查询语句执行,查询所有账户
    sql = "select account_name,account_id,account_key from zero_cloud_user;"
    cursor.execute(sql)
    # 查询结果
    all_info = cursor.fetchall()

    # 查询实例表中所有ip,放在ip_info列表中
    sql2 = "select ip from zero_ins_type;"
    cursor.execute(sql2)
    ip_data = cursor.fetchall()
    ip_info = []
    for i in ip_data:
        ip_info.append(i[0])

    # 遍历账户查询结果
    for info in all_info:
        try:
            # 根据账户名称查询区域region
            sql_region = "select region from zero_account_zone where account_name='%s';" % info[0]
            cursor.execute(sql_region)
            region_name = cursor.fetchone()
            # 将region_name这个大字符串变成列表,并去掉字符串中的空格
            region_name = [x.strip() for x in region_name[0].split(',')]
            # 密钥
            cred = credential.Credential(info[1], info[2])
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cvm.tencentcloudapi.com"

            # 服务器所在大区
            for region in region_name:
                # 根据region中文名在zero_zone_code表中查询中对应代号,code[0](code是数据库查询返回的元组)
                sql_code = "select code from zero_zone_code where zone='%s';" % region
                cursor.execute(sql_code)
                code = cursor.fetchone()

                clientProfile = ClientProfile()
                clientProfile.httpProfile = httpProfile
                client = cvm_client.CvmClient(cred, code[0], clientProfile)

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
                    merge = str(ins_cpu) + '核/' + str(ins_memory) + 'G/' \
                            + str(disk_size) + 'G/' + str(internet_width) + 'Mbps'

                    # 插入数据库
                    str_ip = str(ins_set['PrivateIpAddressed']).replace('[', '').replace(']', '').replace("'", "")

                    # 查看ip是否已经存在，不存在则插入，存在则更新
                    if str_ip not in ip_info:
                        insert_sql = "insert into zero_ins_type(ins_type,ip,account_name) values('%s','%s','%s')" \
                                     % (merge, str_ip, info[0])
                        cursor.execute(insert_sql)
                    else:
                        update_sql = "update zero_ins_type set ins_type='%s' where ip='%s';" % (merge, str_ip)
                        cursor.execute(update_sql)
                    conn.commit()

        except TencentCloudSDKException as err:
            print(err)
            raise err

    # 关闭数据库和游标
    cursor.close()
    conn.close()


if __name__ == "__main__":
    insert()
