#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-

from log.models import BreakLogSearch


def search(server_name, version, zone, plat, run_company, start, end, time_start, time_end):

    if version == "('')" or version == "()":
        count_data = BreakLogSearch.objects.raw("""select server_name,time,max_player,cpu,memory,send_flow,recv_flow,id 
        from zero_break_log_search where (server_name = '%s' or '%s'='') and (zone = '%s' or '%s'='') and 
        (plat = '%s' or '%s' = '') and (run_company = '%s' or '%s' = '') and (time >= '%s' or '%s'='') and 
        (time <='%s' or '%s'='')  and (hour(time)>='%s' or '%s'='') and (hour(time)<'%s' or '%s'='');""" %
                                                (server_name, server_name, zone, zone, plat, plat, run_company,
                                                 run_company, start, start, end, end, time_start, time_start,
                                                 time_end, time_end))
    else:
        count_data = BreakLogSearch.objects.raw("""select server_name,time,max_player,cpu,memory,send_flow,recv_flow,id 
        from zero_break_log_search where (server_name = '%s' or '%s'='') and (version = '%s' or '%s' = '') and 
        (zone = '%s' or '%s'='') and (plat = '%s' or '%s' = '') and (run_company = '%s' or '%s' = '') and 
        (time >= '%s' or '%s'='') and (time <='%s' or '%s'='') and (hour(time)>='%s' or '%s'='') and 
        (hour(time)<'%s' or '%s'='');""" % (server_name, server_name, version, version, zone, zone, plat, plat,
                                            run_company, run_company, start, start, end, end, time_start,
                                            time_start, time_end, time_end))

    return count_data


if __name__ == '__main__':
    search(server_name='', version="('')", zone='Asia/China', plat='ios', run_company='', start='', end='',
           time_start='', time_end='')
