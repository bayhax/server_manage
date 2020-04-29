#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
# import pymysql

from server_list.models import ServerListUpdate


def search(server_name, version, zone, plat, run_company):
    # count = ''
    # # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    # db = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # # 使用 cursor() 方法创建一个游标对象 cursor
    # cursor = db.cursor()

    if version == "('')" or version == "()":
        count_data = ServerListUpdate.objects.raw("""select server_name,max_player,cpu,memory,send_flow,recv_flow,
        version,is_activate from zero_server_list_update where (server_name = '%s' or '%s'='') and 
        (zone = '%s' or '%s'='') and (plat = '%s' or '%s' = '') and (run_company = '%s' or '%s' = '');"""
                                                  % (server_name, server_name, zone, zone, plat, plat, run_company,
                                                     run_company))
        # sql = """select server_name,max_player,cpu,memory,send_flow,recv_flow,version,is_activate
        #         from zero_server_list_update where (server_name = '%s' or '%s'='')and (zone = '%s' or '%s'='')
        #         and (plat = '%s' or '%s' = '') and (run_company = '%s' or '%s' = '');""" \
        #       % (server_name, server_name, zone, zone, plat, plat, run_company, run_company)
    else:
        count_data = ServerListUpdate.objects.raw("""select server_name,max_player,cpu,memory,send_flow,recv_flow,
        version,is_activate from zero_server_list_update where (server_name = '%s' or '%s'='') and 
        (version = '%s' or '%s'='') and (zone = '%s' or '%s'='') and (plat = '%s' or '%s' = '') and
        (run_company = '%s' or '%s' = '');""" % (server_name, server_name, version, version, zone, zone, plat, plat,
                                                 run_company, run_company))
    #     sql = """select server_name,max_player,cpu,memory,send_flow,recv_flow,version,is_activate
    #             from zero_server_list_update where (server_name = '%s' or '%s'='') and (version = '%s' or '%s'='')
    #             and (zone = '%s' or '%s'='') and (plat = '%s' or '%s' = '') and (run_company = '%s' or '%s' = '');"""
    #           % (server_name, server_name, version, version, zone, zone, plat, plat, run_company, run_company)
    # 执行语句
    # cursor.execute(sql)
    # # 使用 fetchone() 方法获取全部数据.
    # count_data = cursor.fetchall()
    #
    # # 关闭数据库连接
    # cursor.close()
    # db.close()

    return count_data


if __name__ == '__main__':
    search(server_name='', version="('')", zone='Asia/China', plat='ios', run_company='')
