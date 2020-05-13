#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
# import pymysql
from apps.cloud_user import search_region
from apps.cloud_user import search_zone
from cloud_user.models import ZoneCode, AccountZone, Account


def insert():

    account_info = Account.objects.all().values_list('account_name', 'account_id', 'account_key', 'id')
    # 遍历账户更新可用区
    for acc in account_info:
        # 总区域
        region, region_name = search_region.search(acc[0], acc[1], acc[2])
        # 将区域插入进数据表
        for i in range(len(region)):
            if not ZoneCode.objects.filter(zone=region_name[i]).exists():
               region_code = ZoneCode(code=region[i], zone=region_name[i])
               region_code.save()

        # 该区域的可用区
        for reg in region:
            zone_code, zone_name = search_zone.search(acc[1], acc[2], reg)
            merge = dict(zip(zone_code, zone_name))
            # 查询zero_zone_code表中是否有该区域
            for key, value in merge.items():
                if not ZoneCode.objects.filter(zone=value).exists():
                    zero_zone_code = ZoneCode(code=key, zone=value)
                    zero_zone_code.save()

        # 获取所有可用区，将可用区变成字符串存到数据库中
        all_available_zone = str(region_name).replace("'", "").replace('[', '').replace(']', '')
        # 如果没有该账户，则插入，否则更新
        if not AccountZone.objects.filter(account_name=acc[0]).exists(): 
            print('--')
            account_zone = AccountZone(account_name=acc[0], account_id=acc[1], account_key=acc[2], region=all_available_zone, cloud_user_id=acc[3])
            account_zone.save()


if __name__ == '__main__':
    insert()
