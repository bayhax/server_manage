#!/root/.virtualenvs/server/bin/python3
# -*- coding:utf-8 -*-
# @Author:bayhax
# import pymysql

from config.models import Pattern
from server_list.models import ServerListUpdate


def search(ip, pattern):
    # 该实例下有几个该模式的服务器
    num = ServerListUpdate.objects.filter(ip=ip, pattern=pattern).count()
    # 获得该实例的类型信息（2核/4G/3Mbps/50G）
    res = Pattern.objects.get(pattern=pattern)
    ins_cpu = int(res.ins_type.split('/')[0].replace('核', ''))
    ins_memory = int(res.ins_type.split('/')[1].replace('G', ''))
    ins_flow = int(res.ins_type.split('/')[2].replace('Mbps', ''))
    ins_disk = int(res.ins_type.split('/')[3].replace('G', ''))
    # 该模式配置时所分配的磁盘大小等信息
    allo_cpu = res.cpu_num
    allo_memory = res.memory_num
    allo_flow = res.flow_num
    allo_disk = res.disk_num

    # 如果memory为空，说明该实例下还没有开设该模式的服务器，则返回可开设的最大台数
    if num == 0:
        c = int(ins_cpu / allo_cpu)
        m = int(ins_memory / allo_memory)
        f = int(ins_flow / allo_flow)
        d = int(ins_disk / allo_disk)
        return min(c, m, f, d)
    else:
        c = int(ins_cpu / allo_cpu) - num
        m = int(ins_memory / allo_memory) - num
        f = int(ins_flow / allo_flow) - num
        d = int(ins_disk / allo_disk) - num
        return min(c, m, f, d)


if __name__ == '__main__':
    search(ip='192.144.238.49', pattern="normal")
