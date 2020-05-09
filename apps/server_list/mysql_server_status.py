#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
from server_list.models import ServerListUpdate


def search(server_name, version, zone, plat, run_company):

    if version == "('')" or version == "()":
        count_data = ServerListUpdate.objects.raw("""select server_name,max_player,cpu,memory,send_flow,recv_flow,
        version,is_activate from zero_server_list_update where (server_name = '%s' or '%s'='') and 
        (zone = '%s' or '%s'='') and (plat = '%s' or '%s' = '') and (run_company = '%s' or '%s' = '');"""
                                                  % (server_name, server_name, zone, zone, plat, plat, run_company,
                                                     run_company))
    else:
        count_data = ServerListUpdate.objects.raw("""select server_name,max_player,cpu,memory,send_flow,recv_flow,
        version,is_activate from zero_server_list_update where (server_name = '%s' or '%s'='') and 
        (version = '%s' or '%s'='') and (zone = '%s' or '%s'='') and (plat = '%s' or '%s' = '') and
        (run_company = '%s' or '%s' = '');""" % (server_name, server_name, version, version, zone, zone, plat, plat,
                                                 run_company, run_company))

    return count_data


if __name__ == '__main__':
    search(server_name='', version="('')", zone='Asia/China', plat='ios', run_company='')
