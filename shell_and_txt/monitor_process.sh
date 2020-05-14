#!/bin/sh
source /etc/profile
uuid=()
# 遍历目前存在的服务器进程号
all_pid=`top -b -n 1 | grep SandBox | awk '{print $1}'`
# 声明字典
declare -A dic
dic=()
# 获取文件名和进程pid对应的键值对
for pid_num in `top -b -n 1 | grep SandBox | awk '{print $1}'`; do
    dic+=([$pid_num]=`cat /proc/$pid_num/fd/1 | grep "Set current" | awk 'END {print $5}'`)
done
# 判断有无该服务器进程
process_judge()
{
    flag="0"
    # 遍历所有文件名
    temp=`echo ${!dic[*]}`
    for key in $temp; do
        result=$(echo ${dic[$key]} | grep $1)
        if [[ "$result" != "" ]]; then
            echo $key
            flag="1"
            break
        fi
    done
    if [[ "$flag" == "0" ]]; then
        echo "0"
    fi
}
# 遍历服务器文件夹，查看服务器文件夹中状态文件flag.txt
for ser in `ls /home/server/`; do
    flag=`cat /home/server/$ser/flag.txt | awk '{print}'`
    # 如果为1，则表示服务器应该正在运行，查看进程是否存在
    if [[ $flag == '1' ]]; then
        res=$(process_judge $ser)
        # cpu状态
        cpu_status=`top -b -n 1 | grep SandBox | awk '{print $9}'`
        # 如果该进程存在
        if [[ "0" != $res ]]; then
            # 查看进程状态
            stat=`cat /proc/$res/status | grep State | awk '{print $2}'`
       
            # cpu占用率小于5但是管道文件可以使用，说明进程没崩溃，只是没有玩家
            if [[ `echo "${cpu_status} < 5" |bc` -eq 1 ]]; then
                # 管道文件位置
                temp_locate="/home/server/"${ser}"/in.pipe"
                # 设置超时时间
                timeout 2 echo 'count' > $temp_locate
                # 记录当前时间和文件时间
                cur_date=`date '+%H:%M'`
                nohup_date=`ls -al "/home/server/"${ser} | grep nohup | awk '{print $8}'`
                pipe_date=`ls -al "/home/server/"${ser} | grep pipe | awk '{print $8}'`
                if [[ "${cur_date}" == "${nohup_date}" ]] || [[ "${cur_date}" == "${pipe_date}" ]]; then
                    continue
                else
                    stat="Z"
                fi
            fi
            if [[ "${stat}" == "Z" ]] || [[ "${stat}" == "D" ]] || [[ `echo "${cpu_status} < 5" |bc` -eq 1 ]]; then
                pid=`cat /proc/$res/status | grep -w Pid | awk '{print $2}'` 
                pipe_pid=$(($pid-1))
                kill $pid
                kill $pipe_pid
                # 获取服务器文件名成uuid,服务器名称
                # uuid=`cat /proc/$pid_num/fd/1 | grep 'Set current' | awk 'END {print $5}'`
                uuid="/home/server/"${ser}
                server_name_temp=`cat ${uuid}"/SandBox_Data/StreamingAssets/Server/Config.txt" | awk 'NR==1 {print $3}'`
                temp1=`echo ${server_name_temp//\"/}`
                temp2=`echo ${temp1//\(/_}`
                server_name=`echo ${temp2//\)/}`
                
                # 备份日志
                # 备份日志文件名组合
                time=`date '+%Y-%m-%d_%H:%M:%S'`
                log_name=${server_name}"_"${time}".log"
                scp ${uuid}"/nohup.out" root@172.22.0.11:/home/log/$log_name
                
                # 发送崩溃时的服务器状态文件
                # 获取内存，cpu，
                cpu=`top -b -n 1 | grep SandBox | grep -w $res | awk '{print $9}'`
                memory=`top -b -n 1 | grep SandBox | grep -w $res | awk '{print $10}'`              
                send_flow="0"
                recv_flow="0"
                break_name=${server_name}"_"${time}".txt"
                # echo ${server_name}" "${cpu}" "${memory}" "${send_flow}" "${recv_flow} > $break_name
                # scp $break_name root@172.22.0.11:/home/break_status
                
                # 重新开启服务器,先进入到服务器文件目录下，执行启动脚本，因为脚本中使用了当前工作路径pwd，防止找不到文件
                cd ${uuid}
                # 确保关掉管道进程
                pipe_pid=`lsof in.pipe | grep in.pipe | awk '{print $2}'`
                kill $pipe_pid
                sh ${uuid}"/start.sh"
                # 将flag.txt文件状态改为1
                echo "1" > /home/server/$ser/flag.txt
                # 再回到当前目录下
                cd /home/time_task
            else
                continue
            fi
        # 如果该服务器进程不存在
        else
            # 获取服务器文件名成uuid,服务器名称
            uuid="/home/server/"${ser}
            server_name_temp=`cat ${uuid}"/SandBox_Data/StreamingAssets/Server/Config.txt" | awk 'NR==1 {print $3}'`
            temp1=`echo ${server_name_temp//\"/}`
            temp2=`echo ${temp1//\(/_}`
            server_name=`echo ${temp2//\)/}`
           
            # 备份日志
            # 备份日志文件名组合
            time=`date '+%Y-%m-%d_%H:%M:%S'`
            log_name=${server_name}"_"${time}".log"
           
            # 发送最近一次的服务器状态文件
            # 在管理服务器的实例上获取即可            
            # 文件名有特殊字符括号,在上方将服务器文件名特殊字符替换
            scp ${uuid}"/nohup.out" root@172.22.0.11:/home/log/$log_name
           
            # 重新开启服务器
            cd ${uuid}
            # 确保关掉管道进程
            pipe_pid=`lsof in.pipe | grep in.pipe | awk '{print $2}'`
            kill $pipe_pid
           
            sh ${uuid}"/start.sh"
            # 将flag.txt文件状态改为1
            echo "1" > /home/server/$ser/flag.txt
            cd /home/time_task
        fi
    fi 
done
# 清空pid服务器名称文件
pri_ip=`ifconfig eth0 | grep -w inet | grep -v grep | awk '{print $2}'`
filename="/home/time_task/pid_server_"${pri_ip}".txt"
if [ -f $filename ]; then
    rm -f $filename
fi
# 最新的服务器名称和pid 文件
for pid_num in `top -b -n 1 | grep SandBox | awk '{print $1}'`; do
    # 获取服务器文件名成uuid,服务器名称
    uuid=`cat /proc/$pid_num/fd/1 | grep "Set current" | awk 'END {print $5}'`
    server_name_temp=`cat ${uuid}"/SandBox_Data/StreamingAssets/Server/Config.txt" | awk 'NR==1 {print $3}'`
    server_name=`echo ${server_name_temp//\"/}`
    echo ${pid_num}" "${server_name} >> $filename
done
scp $filename root@172.22.0.11:/home/pid_server/
