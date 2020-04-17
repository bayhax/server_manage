#!/root/.virtualenvs/server/bin/python3
####################
#    Author: bayhax
####################
import os
import pexpect
import paramiko


def install(ip, user):
    # 作互信机制
    cmd = "ssh-copy-id -i /root/.ssh/id_rsa.pub root@%s" % ip
    child = pexpect.spawn(cmd)
    index = child.expect(["Are you sure you want to continue connecting", pexpect.EOF, pexpect.TIMEOUT])
    if index == 0:
        child.sendline('yes')
        p = child.expect(["(?i)password", pexpect.EOF, pexpect.TIMEOUT])
        if p == 0:
            child.sendline('2wsxZAQ!')
        else:
            print('连接超时或其他原因')
            child.close()
    else:
        print("已经建立互信")
        child.close()
    os.system(cmd)
    # ssh建立连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh.connect(
        hostname=ip,
        username=user
    )
    # 生成id_rsa.pub发送回来，实现双向互信
    ssh_key_cmd = "ssh-keygen -t rsa"
    temp = ssh.exec_command(ssh_key_cmd)
    send_cmd = "scp root@%s:/root/.ssh/id_rsa.pub /home" % ip
    tmep = ssh.exec_command(send_cmd)
    # 将pub公共密钥放在认证文件中
    copy_key = "cat /home/id_rsa.pub >> /root/.ssh/authorized_keys"
    os.system(copy_key)
    # 删除发送过来的公钥文件
    rm_key = "rm /home/id_rsa.pub"
    os.system(rm_key)
    # 判断防火墙是否已经开启，若没有开启，则开启防火墙
    # firewall_stat_cmd = "firewall-cmd --state"
    # stdin, stdout, stderr = ssh.exec_command(firewall_stat_cmd)
    # firewall_stat = stdout.read().decode('utf-8').strip()
    # if firewall_stat != "running":
    #     # 开启防火墙
    #     start_firewall_cmd = "systemctl start firewalld"
    #     ssh.exec_command(start_firewall_cmd)
    # 安装必要模块，（nethogs,curl,作ssh互信机制）,建立虚拟内存
    nethogs_cmd = "yum install nethogs -y"
    stdin, stdout, stderr = ssh.exec_command(nethogs_cmd)
    temp = stdout.read().decode('utf-8')
    # 安装curl
    curl_cmd = "yum install curl -y"
    stdin, stdout, stderr = ssh.exec_command(curl_cmd)
    temp = stdout.read().decode('utf-8')
    # 设置虚拟内存,暂时不用
    # 检测是否已经设置了虚拟内存
    # judge_swap_cmd = "free -m | grep Swap | awk '{print $2}'"
    # stdin, stdout, stderr = ssh.exec_command(judge_swap_cmd)
    # if stdout.read().decode('utf-8').strip() == '0':
    #     # 没有创建虚拟内存，则进行虚拟内存的创建,2G,swapfile并挂载
    #     swap_cmd = "dd if=/dev/zero of=/home/swapfile bs=1024 count=2048000;mkswap -f /home/swapfile;" \
    #                "swapon /home/swapfile;"
    #     ssh.exec_command(swap_cmd)
    #     # 设置永久挂载
    #     mount_cmd = "echo '/home/swapfile swap swap default 0 0' >> /etc/fstab"
    #     ssh.exec_command(mount_cmd)
    # 判断/home/server是否存在
    # is_exist = "[ -d /home/server ] && echo 'found' || echo 'not found'"
    # stdin, stdout, stderr = ssh.exec_command(is_exist)
    # if stdout.read().decode('utf-8').strip() == "not found":
    #     mkserver = "mkdir /home/server"
    # 建立相关的目录，/home/server  /home/time_task  /home/log
    mk = "mkdir /home/server; mkdir /home/time_task;"
    stdin, stdout, stderr = ssh.exec_command(mk)
    temp = stdout.read().decode('utf-8')
    # 拷贝定时任务文件到实例（monitor_process.sh, server_status.sh,设置为定时任务）
    copy_monitor = "scp /home/server/monitor_process.sh root@%s:/home/time_task" % ip
    os.system(copy_monitor)
    copy_status = "scp /home/server/server_status.sh root@%s:/home/time_task" % ip
    os.system(copy_status)
    copy_time = "scp /home/server/time.txt root@%s:/home/time_task" % ip
    os.system(copy_time)
    # 添加定时任务
    add_time_task = "crontab /home/time_task/time.txt; rm -f /home/time_task/time.txt"
    stdin, stdout, stderr = ssh.exec_command(add_time_task)
    temp = stdout.read().decode('utf-8')
    ssh.close()


if __name__ == "__main__":
    install(ip='106.52.72.50', user='root')
