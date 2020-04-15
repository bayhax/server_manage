#!/root/.virtualenvs/server/bin/python3
# -*- coding:utf-8 -*-
# @Author:bayhax
import pymysql


def search(ip, pattern):
    # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    conn = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()

    sql = """select count(*) from zero_server_list_update where ip='%s' and pattern = '%s';""" % (ip, pattern)

    cursor.execute(sql)
    num = cursor.fetchone()

    alloc_sql = """select ins_type,cpu_num,memory_num,flow_num,disk_num from zero_pattern where pattern = '%s';""" \
                % pattern
    cursor.execute(alloc_sql)
    res = cursor.fetchone()
    ins_cpu = int(res[0].split('/')[0].replace('核', ''))
    ins_memory = int(res[0].split('/')[1].replace('G', ''))
    ins_flow = int(res[0].split('/')[3].replace('Mbps', ''))
    ins_disk = int(res[0].split('/')[2].replace('G', ''))
    all_cpu = res[1]
    all_memory = res[2]
    all_flow = res[3]
    all_disk = res[4]

    # 关闭数据库连接
    cursor.close()
    conn.close()
    # 如果memory为空，说明该实例下还没有开设该模式的服务器，则返回可开设的最大台数
    if num[0] == 0:
        c = int(ins_cpu / all_cpu)
        m = int(ins_memory / all_memory)
        f = int(ins_flow / all_flow)
        d = int(ins_disk / all_disk)
        return min(c, m, f, d)
    else:
        c = int(ins_cpu / (all_cpu * num[0]))
        m = int(ins_memory / (all_memory * num[0]))
        f = int(ins_flow / (all_flow * num[0]))
        d = int(ins_disk / (all_disk * num[0]))
        return min(c, m, f, d)


if __name__ == '__main__':
    search(ip='192.144.238.49', pattern="normal")
