#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import pymysql

def insert_update():
     # 打开数据库连接（ip/数据库用户名/登录密码/数据库名）
    conn = pymysql.connect("localhost", "root", "P@ssw0rd1", "zero_server")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()
    
    server_list_server_name = []
    server_list_update_server_name = []
    # 在zero_server_list表中查询中定时更新的五分钟内的所有服务器名称
    sql = """select server_name from zero_server_list where time >= date_add(now(),interval -5 minute);"""
    cursor.execute(sql)
    data = cursor.fetchall()
    for d in data:
        server_list_server_name.append(d[0])

    # zero_server_list_update表中所有服务器名称
    sql2 = """select server_name from zero_server_list_update;"""
    cursor.execute(sql2)
    data2 = cursor.fetchall()
    for d in data2:
        server_list_update_server_name.append(d[0])

    # 查看该服务器在zero_server_list_update表中是否存在
    for name in server_list_server_name:
        # 存在则更新
        if name in server_list_update_server_name:
            update_sql = """update zero_server_list_update a,zero_server_list b set a.max_player=b.max_player,a.cpu=b.cpu,a.memory=b.memory,a.flow=b.flow,a.version=b.version,
                            a.pattern=b.pattern,a.zone=b.zone,a.plat=b.plat,a.run_company=b.run_company,a.ip=b.ip,a.user=b.user,a.port=b.port,a.instance_name=b.instance_name,
                            a.account=b.account,a.time=b.time where a.server_name=b.server_name and b.time >= date_add(now(),interval -5 minute);"""
            cursor.execute(update_sql)
        # 不存在则插入
        else:
            insert_sql = """insert into zero_server_list_update(server_name,max_player,cpu,memory,flow,version,pattern,zone,plat,run_company,ip,user,port,instance_name,account,time)
                            select server_name,max_player,cpu,memory,flow,version,pattern,zone,plat,run_company,ip,user,port,instance_name,account,time 
                            from zero_server_list where server_name = '%s' and time >= date_add(now(),interval -5 minute);""" % name
            cursor.execute(insert_sql)
        
        # 提交
        conn.commit()


    cursor.close()
    # 关闭数据库连接
    conn.close()

if __name__ == "__main__":
    # server_name/command
    insert_update()
