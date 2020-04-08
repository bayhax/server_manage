#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import os
import pymysql


def monitor():
    # # 数据库连接
    conn = pymysql.connect('localhost', 'root', 'P@ssw0rd1', 'zero_server')
    # 创建游标对象
    cursor = conn.cursor()
    # 读取/home/pid_server/文件夹下的所有文件，
    server_name_sql = "select server_name from zero_server_pid;"
    cursor.execute(server_name_sql)
    server_name = [x[0] for x in cursor.fetchall()]
    for file in os.listdir("/home/pid_server/"):
        with open("/home/pid_server/" + file, 'r') as f:
            data = f.readlines()
            ip = file.replace('.txt', '').split('_')[2]
            data_pid = [x.split(' ')[0] for x in data]
            print(data_pid)
            data_server_name = [x.split(' ')[1].replace('\n', '') for x in data]
            for i in range(len(data_server_name)):
                if data_server_name[i] in server_name:
                    pid_sql = """select pid from zero_server_pid where server_name = '%s';""" % data_server_name[i]
                    cursor.execute(pid_sql)
                    if data_pid[i] != cursor.fetchone()[0]:
                        # 在log文件夹下，找出该服务器的最新崩溃日志时间
                        cmd = "ls -ltr /home/log | grep %s | awk 'END {print}'" % \
                              data_server_name[i].replace('(', '_').replace(')', '') + '_'
                        latest_time = os.popen(cmd)
                        # 读取之后就消失,最新时间
                        time_temp = latest_time.read().split(' ')[-1].replace('\n', '').split('_')[3:5]
                        print(time_temp)
                        time = time_temp[0] + ' ' + time_temp[1].replace('.log', '')
                        # 在break_status文件下查找如果没有该时间，则将zero_server_list_update表的数据插入，time改为崩溃日志的时间
                        # 该进程已经死亡，则将之前数据插入到zero_break_log_search表中，
                        sql_select = """select server_name,max_player,cpu,memory,send_flow,recv_flow,version,zone,plat,
                                    run_company,ip,user from zero_server_list_update where server_name='%s';""" \
                                     % data_server_name[i]
                        cursor.execute(sql_select)
                        temp_data = cursor.fetchone()
                        sql_update = """insert into zero_break_log_search(server_name,max_player,cpu,memory,send_flow,
                                    recv_flow,version,zone,plat,run_company,ip,user,time) values('%s','%s','%s','%s',
                                    '%s','%s','%s','%s','%s','%s','%s','%s','%s')""" \
                                     % (temp_data[0], temp_data[1], temp_data[2], temp_data[3], temp_data[4],
                                        temp_data[5], temp_data[6], temp_data[7], temp_data[8], temp_data[9],
                                        temp_data[10], temp_data[11], time)
                        cursor.execute(sql_update)
                        sql = """update zero_server_pid set pid=%s where server_name='%s';""" \
                              % (data_pid[i], data_server_name[i])
                        cursor.execute(sql)
                        conn.commit()
                # 误删操作
                else:
                    sql = """insert into zero_server_pid(server_name,pid,ip,user,flag)
                                values('%s','%s','%s','%s',1)""" % (data_server_name[i], data_pid[0], ip, 'root')

                    cursor.execute(sql)
                    conn.commit()
    # 关闭数据库连接和ssh连接
    cursor.close()
    conn.close()


if __name__ == "__main__":
    monitor()
