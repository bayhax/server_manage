#!/root/.virtualenvs/server/bin/python3
# -*- coding: utf-8 -*-
# import pymysql

from log.models import BreakLogSearch


def search(server_name, start, end):

    count_data = BreakLogSearch.objects.filter(server_name=server_name,
                                               time_gt=start, time_lt=end).values_list('time', 'max_player', 'cpu',
                                                                                       'memory', 'send_flow',
                                                                                       'recv_flow')
    return count_data


if __name__ == '__main__':
    search(server_name='删档测试二服', start='2020-02-29 12:00', end="2020-02-29 14:00")
