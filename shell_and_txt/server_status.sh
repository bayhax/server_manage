#!/bin/sh
# 刷新以下环境变量，不然定时任务找不到ip地址，不能使用环境变量
source /etc/profile
top -b -n 1 | grep SandBox > /home/time_task/cpu_memory.txt  # 进程号  cpu memory
nethogs -v 2 -c 3 -d 2 -t | grep SandBox > /home/time_task/flow.txt  # 流量信息
# 本机公网ip
# ip=`curl ip.sb | awk 'END {print}'`
# 内网ip
pri_ip=`ifconfig eth0 | grep -w inet | awk '{print $2}'`
filename="/home/time_task/merge_info_"${pri_ip}".txt"
echo $filename
if [ -f $filenmae ]; then
    rm -f $filename
fi
# 循环获取每个服务器的在线人数，cpu,memory,send_flow,recv_flow信息
for pid_num in `awk '{print $1}' /home/time_task/cpu_memory.txt`; do
    uuid=`cat /proc/$pid_num/fd/1 | grep "Set current" | awk 'END {print $5}'`
    name=${uuid}"/in.pipe" 
    echo 'count' > $name
    online_temp=`cat ${uuid}"/nohup.out" | awk 'END {print}'`
    online=`echo ${online_temp} | sed 's/ //g'`
    # echo $online
    # if [[ ${#online} > 5 ]]; then
    #     $online="0"
    # fi
    cpu=`cat /home/time_task/cpu_memory.txt | grep $pid_num | awk '{print $9}'`
    memory=`cat /home/time_task/cpu_memory.txt | grep $pid_num | awk '{print $10}'`
    send_flow=`cat /home/time_task/flow.txt | grep $pid_num | awk 'END {print $2}'`
    if [ ! $send_flow ]; then
        send_flow=0
    fi
    recv_flow=`cat /home/time_task/flow.txt | grep $pid_num | awk 'END {print $3}'`
    if [ ! $recv_flow ]; then
        recv_flow=0
    fi
    server_name_temp=`cat ${uuid}"/SandBox_Data/StreamingAssets/Server/Config.txt" | awk 'NR==1 {print $3}'`
    server_name=`echo ${server_name_temp//\"/}`
    server_port_temp=`cat ${uuid}"/SandBox_Data/StreamingAssets/Server/Config.txt" | awk 'NR==2 {print $3}'`
    server_port=`echo ${server_port_temp//\"/}`

    max_player_temp=`cat ${uuid}"/SandBox_Data/StreamingAssets/Server/Config.txt" | awk 'END {print $3}'`
    max_player=`echo ${max_player_temp//\"/}`
    echo ${server_name}" "${server_port}" "${max_player}" "${pid_num}" "${online}" "${cpu}" "${memory}" "${send_flow}" "${recv_flow} >> $filename
    
    # 监测nohup日志中是否有Exception关键字，如果有，则将日志发送到管理服务器的实例，
    line=`cat /home/time_task/variable | grep ${server_name}"_monitor"`
    if [[ $line != "" ]]; then
        line_num=`echo $line | awk -F= '{print $2}'`
    else
        line_num=0
    fi
    test=`cat ${uuid}"/nohup.out" | tail -n +${line_num} | grep Exception`
    # 此次查看时日志有多少行,只要行数
    line=`wc -l ${uuid}"/nohup.out" | awk '{print $1}'`
    # 删除变量
    variable_num=`cat /home/time_task/variable | grep -n ${server_name}"_monitor" | awk -F: '{print $1}'`
    if [[ $variable_num != '' ]]; then
        # echo ${variable_num}"d"
        sed -i ${variable_num}"d" /home/time_task/variable
    fi
    # 更新环境变量
    temp_monitor="_monitor"
    echo "${server_name}${temp_monitor}=$line" >> /home/time_task/variable
    if [[ $test != "" ]]; then
        # 组文件名称
        temp2=`echo ${server_name//\(/_}`
        temp_log=`echo ${temp2//\)/}`
        time=`date '+%Y-%m-%d_%H:%M:%S'`
        log_name=${temp_log}"_"${time}".log"
        scp ${uuid}"/nohup.out" root@172.22.0.11:home/log/$log_name
    fi
done
# 向管理服务器的实例发送信息文件
scp $filename root@172.22.0.11:/home/time_task/

