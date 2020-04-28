#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
import pymysql
from apps.cloud_user import search_region
from apps.cloud_user import search_zone


def insert():
    # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    db = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    sql = """select account_name,account_id,account_key,id from zero_cloud_user;"""

    # 查询所有账户
    cursor.execute(sql)
    account_info = cursor.fetchall()

    # 遍历账户更新可用区
    for acc in account_info:
        # 总区域
        region, region_name = search_region.search(acc[0], acc[1], acc[2])
        # 将区域插入进数据表
        for i in range(len(region)):
            search_sql = """select count(*) from zero_zone_code where zone='%s';""" % region_name[i]
            cursor.execute(search_sql)
            count = cursor.fetchone()
            # 如果没有该名称，则插入，否则更新
            if count[0] == 0:
                insert_sql = """insert into zero_zone_code(code,zone) values('%s','%s');"""\
                             % (region[i], region_name[i])
                cursor.execute(insert_sql)
            else:
                update_sql = """update zero_zone_code set code='%s' where zone='%s';""" % (region[i], region_name[i])
                cursor.execute(update_sql)
            db.commit()

        # 该区域的可用区
        for reg in region:
            zone_code, zone_name = search_zone.search(acc[1], acc[2], reg)
            merge = dict(zip(zone_code, zone_name))
            # 查询zero_zone_code表中是否有该区域
            for key, value in merge.items():
                search_sql = """select count(*) from zero_zone_code where zone='%s';""" % value
                cursor.execute(search_sql)
                count = cursor.fetchone()
                # 如果没有该名称，则插入，否则更新
                if count[0] == 0:
                    insert_sql = """insert into zero_zone_code(code,zone) values('%s','%s');""" % (key, value)
                    cursor.execute(insert_sql)
                else:
                    update_sql = """update zero_zone_code set code='%s' where zone='%s';""" % (key, value)
                    cursor.execute(update_sql)
                db.commit()

        # 获取所有可用区，将可用区变成字符串存到数据库中
        all_available_zone = str(region_name).replace("'", "").replace('[', '').replace(']', '')
        search_sql = """select count(*) from zero_account_zone where account_name='%s';""" % acc[0]
        cursor.execute(search_sql)
        count2 = cursor.fetchone()
        # 如果没有该账户，则插入，否则更新
        if count2[0] == 0:
            insert_sql2 = """insert into zero_account_zone(account_name,account_id,account_key,region,cloud_user_id)
                            values('%s','%s','%s','%s',%d);""" % (acc[0], acc[1], acc[2], all_available_zone, acc[3])
            cursor.execute(insert_sql2)
        else:
            update_sql2 = """update zero_account_zone set region='%s' where account_name='%s';""" \
                          % (all_available_zone, acc[0])
            cursor.execute(update_sql2)
        db.commit()

    cursor.close()
    # 关闭数据库连接
    db.close()


if __name__ == '__main__':
    insert()
