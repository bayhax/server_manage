#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import os
import uuid

import pymysql


def insert_mysql(dirname):

    # 数据库信息
    conn = pymysql.connect('localhost','root','P@ssw0rd1','zero_server')

    # 创建游标
    cursor = conn.cursor()
    while True:
        # 获取uuid
        uid = uuid.uuid1()
        uid = str(uid).replace('-','')
    
        # sql语句
        sql = """select count(*) from zero_dirname_version where dirname = '%s';""" % uid
        # 执行语句，获取文件名是否存在
        cursor.execute(sql) 
        data = cursor.fetchone()

        if data[0] == 0:
            # 更改唯一文件名
            cmd = "mv /home/server/%s /home/server/%s" % (dirname,uid)
            os.system(cmd)

            # 将启动服务器命令脚本拷贝至文件内
            cmd_start = "cp /home/server/start.sh /home/server/%s" % uid
            os.system(cmd_start)
            
            # 获取服务器名称
            ser_name_cmd = "awk 'NR==1 {print $3}' /home/server/%s/SandBox_Data/StreamingAssets/Server/Config.txt" % uid
            server_name = os.popen(ser_name_cmd).read().replace('"','').strip()
            
            # 存入数据库
            insert_sql = """insert into zero_dirname_version(dirname,version,server_name) values('%s','%s','%s')""" % (uid,'1.0',server_name)
            cursor.execute(insert_sql)
            conn.commit()
            
            # 结束
            break
    
    # 关闭数据库
    cursor.close()
    conn.close()


if __name__ == "__main__":
    # 文件名称
    insert_mysql(dirname='LinuxServer')

