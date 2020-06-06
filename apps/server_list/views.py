from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
from django.core.cache import cache
from django_redis import get_redis_connection
from django.views import View

import os
import json
import time
import datetime
import re

from cloud_user.models import ServerAccountZone, Account
from config.models import AddVersion, Pattern, Version, RunCompany
from log.models import BreakLogSearch
from server_list.models import CommandLog, InsType, ServerPid, ServerListUpdate, ServerNameRule

from apps.server_list import real_time_account_ip, monitor_ins_status, install_and_mkdir, update_server
from apps.server_list import data_count, data_tendency
from apps.server_list import open_server, quit_server, start_server
from apps.server_list import buy_search_instype, buy_inquery_price, buy_ins
from apps.server_list import mysql_server_status
from apps.server_list import send_command_one
from apps.server_list import batch_add_memory
from apps.server_list import batch_add_start_server
from apps.server_list import insert_server_update
from apps.server_list import update_kill_old


# 服务器列表首页
def index(request):
    """服务器列表首页"""
    online_player = 0
    busy_server = 0
    relax_server = 0
    pattern = []
    zone = []
    platform = []
    run_company = []
    version = []
    ip = []
    # 组表头信息
    title = ["server_name", "player", "CPU", "memory", "send_flow", "recv_flow", "version", "is_activate"]
    # 返回页面的字典数据
    fina = []
    redis_conn = get_redis_connection("default")
    
    # 所有的服务器
    server_num = redis_conn.keys('server*')
    # 服务器个数
    count = len(server_num)
    # 取出所需要的服务器信息
    for sn in server_num:
        server_data = redis_conn.hmget(sn.decode('utf-8'), 'pattern', 'zone', 'plat', 'run_company', 'max_player',
                                       'server_name', 'cpu', 'memory', 'send_flow', 'recv_flow', 'version',
                                       'is_activate', 'ip')
        server_data = [x.decode('utf-8') for x in server_data]
        pattern.append(server_data[0])
        version.append(server_data[10])
        zone.append(server_data[1])
        platform.append(server_data[2])
        run_company.append(server_data[3])
        ip.append(server_data[12])
        online = int(server_data[4].split('/')[0])
        online_player += online
        # 判断是否繁忙
        if online / int(server_data[4].split('/')[1]) > 1 / 2:
            busy_server += 1
        else:
            relax_server += 1
        one_server_info = [server_data[5], server_data[4], server_data[6], server_data[7], server_data[8],
                           server_data[9], server_data[10], server_data[11]]
        temp = dict(zip(title, one_server_info))
        fina.append(temp)
    # 查询数据库中可以更新的版本号,查询版本号，flat只要version值，列表，不取key
    update_version_exist = AddVersion.objects.values_list('version', flat=True)

    # 查询数据库中可迁移的模式
    migrate_pattern_exist = Pattern.objects.values_list('pattern', flat=True)

    # 去重
    zone = list(set(zone))
    platform = list(set(platform))
    version = list(set(version))
    run_company = list(set(run_company))
    # 将服务器的分配cpu，内存，实例cpu，内存等信息组合
    instance_allocate = ['cpu_allocate', 'cpu_instance', 'memory_allocate', 'memory_instance', 'flow_allocate',
                         'flow_instance']
    server_config = []
    for i in range(len(pattern)):
        allocate = Pattern.objects.get(pattern=pattern[i])
        # # 该服务器所在实例的实例类型
        instance_type = InsType.objects.get(ip=ip[i]).ins_type
        # 利用正则表达式将实例配置的数字取出来
        instance_type = re.findall(r"\d+\.?\d*", instance_type)
        one_server_config = [allocate.cpu_num, instance_type[0], allocate.memory_num, instance_type[1],
                             allocate.flow_num, instance_type[2]]
        temp = dict(zip(instance_allocate, one_server_config))
        server_config.append(temp)

    # 浏览器显示内容，instance,server为给浏览器返回的内容
    return render(request, 'server_list.html',
                  {'data': fina, 'count_server': count, 'player_count': online_player, 'busy_server': busy_server,
                   'relax_server': relax_server, 'zone': zone, 'platform': platform, 'run_company': run_company,
                   'version': version, 'update_version_exist': update_version_exist, 'pattern': pattern,
                   'migrate_pattern_exist': migrate_pattern_exist, 'server_config': server_config})


# 刷新按钮
# noinspection PyUnusedLocal
def refresh(request):
    redis_conn = get_redis_connection('default')
    # 繁忙台数/空闲台数/在线人数 初始化
    busy_server = 0
    relax_server = 0
    online_player = 0
    # 在zero_server_list_update表中获取所有状态is_activate为1的运行中的服务器，发送命令获取在线人数
    # 运行中的服务器总台数
    # count = ServerListUpdate.objects.filter(is_activate=1).count()
    count = ServerPid.objects.filter(flag=1).count()
    server_rule_id = ServerPid.objects.filter(flag=1).values_list('server_rule_id')
    for rule_id in server_rule_id:
        data = redis_conn.hmget('server:%d' % rule_id, 'server_name', 'ip', 'user', 'max_player')
        data = [x.decode('utf-8') for x in data]
        # 查询出服务器名称，ip,user
        # data = ServerListUpdate.objects.filter(is_activate=1).values_list('server_name', 'ip', 'user', 'max_player')
        # 循环获取每个服务器的在线人数
        for info in data:
            uuid = Version.objects.get(server_name=info[0]).filename_uuid
            # 获取在线人数
            online = int(info[3].split('/')[0])
            # online = int(stdout.read().decode('utf-8').strip())
            online_player += online
            # 判断是否繁忙
            if online / int(info[3].split('/')[1]) > 1 / 2:
                busy_server += 1
            else:
                relax_server += 1

    result = [count, online_player, relax_server, busy_server]
    return HttpResponse(result)


# 查询显示服务器台数和服务器状态等信息
def search(request):
    # 服务器繁忙台数/空闲台数/在线人数初始化
    busy_server = 0
    relax_server = 0
    online_player = 0

    # 获取前端查询条件
    server_name = request.POST['server_name']
    vers = request.POST['vers']
    zones = request.POST['zos']
    plats = request.POST['plats']
    runs = request.POST['runs']

    # 数据库查询，返回元组
    if server_name == '':
        status = ServerListUpdate.objects.filter(version=vers, zone=zones, plat=plats, run_company=runs).values_list(
            'server_name', 'max_player', 'cpu', 'memory', 'send_flow', 'recv_flow', 'version', 'is_activate')
        pattern = ServerListUpdate.objects.filter(version=vers, zone=zones, plat=plats, run_company=runs).values_list(
            'pattern', flat=True)
        ip = ServerListUpdate.objects.filter(version=vers, zone=zones, plat=plats,
                                             run_company=runs).values_list('ip', flat=True)
    else:
        status = ServerListUpdate.objects.filter(server_name=server_name, version=vers, zone=zones, plat=plats,
                                                 run_company=runs).values_list('server_name', 'max_player', 'cpu',
                                                                               'memory', 'send_flow',
                                                                               'recv_flow', 'version', 'is_activate')
        pattern = ServerListUpdate.objects.filter(server_name=server_name, version=vers, zone=zones, plat=plats,
                                                  run_company=runs).values_list('pattern', flat=True)
        ip = ServerListUpdate.objects.filter(server_name=server_name, version=vers, zone=zones, plat=plats,
                                             run_company=runs).values_list('ip', flat=True)
    # 表头信息
    title = ["server_name", "player", "CPU", "memory", "send_flow", "recv_flow", "version", "is_activate"]
    # 返回页面的字典数据
    fina = []
    # 服务器模式分配和实例的相关信息
    server_config = []
    # 组json字符串(按表头字段)
    for st in status:
        # 表格中每一行的数据
        one_server_info = [st[0], st[1], st[2], st[3], st[4], st[5], st[6], st[7]]
        temp = dict(zip(title, one_server_info))
        fina.append(temp)
        # uuid = Version.objects.get(server_name=st[0]).filename_uuid
        data = ServerListUpdate.objects.get(server_name=st[0])
        # 获取在线人数
        online = int(data.max_player.split('/')[0])
        # online = int(stdout.read().decode('utf-8').strip())
        online_player += online
        # 判断是否繁忙
        if online / int(data.max_player.split('/')[1]) > 1 / 2:
            busy_server += 1
        else:
            relax_server += 1

        # 将服务器的分配cpu，内存，实例cpu，内存等信息组合
        instance_allocate = ['cpu_allocate', 'cpu_instance', 'memory_allocate', 'memory_instance', 'flow_allocate',
                             'flow_instance']

        for i in range(len(pattern)):
            allocate = Pattern.objects.get(pattern=pattern[i])
            # # 该服务器所在实例的实例类型
            instance_type = InsType.objects.get(ip=ip[i]).ins_type
            # 利用正则表达式将实例配置的数字取出来
            instance_type = re.findall(r"\d+\.?\d*", instance_type)
            one_server_config = [allocate.cpu_num, instance_type[0], allocate.memory_num, instance_type[1],
                                 allocate.flow_num, instance_type[2]]
            temp = dict(zip(instance_allocate, one_server_config))
            server_config.append(temp)
    # 组python字典，json串传给前端
    res = {'fina': fina, 'count': len(status), 'online_player': online_player, 'relax_server': relax_server,
           'busy_server': busy_server, 'server_config': server_config}
    return HttpResponse(json.dumps(res))


# 选择
def select(request):
    select_server = json.loads(request.POST['select_server'])
    select_server_name = []
    for server in select_server:
        select_server_name.append(server['server_name'])
    # 设置redis缓存系统，为下面试图函数调用的时候使用，select_server_name,list
    cache.set('select_server_name', select_server_name)
    r = HttpResponse(json.dumps('bingo'))  # 查询结果正确
    return r


# 统计页面
def statistics(request):
    # 选择的服务器，
    select_server_name = cache.get('select_server_name')
    # 调用数据模块获取数据
    series, max_player, cpu_allocate, cpu_instance, memory_allocate, memory_instance, flow_allocate, flow_instance, \
        time_line = data_count.day_count(day=7, tyflag=-2, start='', dur=0, server=select_server_name)

    return render(request, 'statistics.html', {'name': select_server_name, 'time_line': time_line, 'series': series,
                                               'max_player': max_player, 'cpu_allocate': cpu_allocate,
                                               'cpu_instance': cpu_instance, 'memory_allocate': memory_allocate,
                                               'memory_instance': memory_instance, 'flow_allocate': flow_allocate,
                                               'flow_instance': flow_instance})


# 统计
class CountView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_name = cache.get('select_server_name')
    
    def post(self, request):
        span = request.POST['span']
        dur = 0
        day = 0
        tyflag = -2
        start = ''
        if span == "seven":
            day = 7
        elif span == "today":
            tyflag = 0
        elif span == "yesterday":
            tyflag = -1
        elif span == "thirty":
            day = 30
        else:
            start_day = request.POST['start']
            end_day = request.POST['end']
            # 将字符串变成日期类型
            st = datetime.datetime.strptime(start_day, '%Y-%m-%d')
            en = datetime.datetime.strptime(end_day, '%Y-%m-%d')
            # 相隔天数
            dur_temp = en - st
            dur_day = dur_temp.days
            dur_day += 1
            start = start_day
            dur = dur_day
       
        series, max_player, cpu_allocate, cpu_instance, memory_allocate, memory_instance, flow_allocate, flow_instance,\
            time_line = data_count.day_count(day=day, tyflag=tyflag, start=start, dur=dur, server=self.server_name)

        return HttpResponse(json.dumps({'time_line': time_line,
                                        'series': series, 'max_player': max_player,
                                        'cpu_allocate': cpu_allocate, 'cpu_instance': cpu_instance,
                                        'memory_allocate': memory_allocate, 'memory_instance': memory_instance,
                                        'flow_allocate': flow_allocate, 'flow_instance': flow_instance}))


# 服务器详情统计
class DetailCountView(CountView):
    def __init__(self):
        CountView.__init__(self)
        self.server_name = cache.get('detail_server_name')

    def post(self, request):
        return super().post(request)


# 趋势
class TendencyView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_name = cache.get('select_server_name')

    def post(self, request):
        span = request.POST['span']
        # 选择的服务器，
        dur = 0
        day = 0
        tyflag = -2
        start = ''
        if span == "seven":
            day = 7
        elif span == "today":
            tyflag = 0
        elif span == "yesterday":
            tyflag = -1
        elif span == "thirty":
            day = 30
        else:
            start_day = request.POST['start']
            end_day = request.POST['end']
            # 将字符串变成日期类型
            st = datetime.datetime.strptime(start_day, '%Y-%m-%d')
            en = datetime.datetime.strptime(end_day, '%Y-%m-%d')
            # 相隔天数
            dur_temp = en - st
            dur_day = dur_temp.days
            dur_day += 1
            start = start_day
            dur = dur_day

        series, max_player, cpu_allocate, cpu_instance, memory_allocate, memory_instance, flow_allocate, flow_instance,\
            time_line = data_tendency.tendency(day=day, tyflag=tyflag, start=start, dur=dur, server=self.server_name)

        return HttpResponse(json.dumps({'time_line': time_line,
                                        'series': series, 'max_player': max_player,
                                        'cpu_allocate': cpu_allocate, 'cpu_instance': cpu_instance,
                                        'memory_allocate': memory_allocate, 'memory_instance': memory_instance,
                                        'flow_allocate': flow_allocate, 'flow_instance': flow_instance}))


# 服务器详情趋势
class DetailTendencyView(TendencyView):
    def __init__(self):
        TendencyView.__init__(self)
        self.server_name = cache.get('detail_server_name')

    @method_decorator(csrf_exempt)
    def post(self, request):
        return super().post(request)


def server_log(request):
    server_break = request.POST['server_break']
    detail_server_name = [server_break]
    # 放入缓存cache
    cache.set('detail_server_name', detail_server_name)
    return HttpResponse('bingo')


# 服务器详情-崩溃日志页面
def break_log(request):
    detail_server_name = cache.get('detail_server_name')
    data = BreakLogSearch.objects.filter(server_name=detail_server_name[0]).values_list('time', 'max_player', 'cpu',
                                                                                        'memory', 'send_flow',
                                                                                        'recv_flow')
    pattern_ip = ServerListUpdate.objects.get(server_name=detail_server_name[0])
    # 表头信息
    title = ["time", "player", "CPU", "memory", "send_flow", "recv_flow"]
    fina = []
    # 组json字符串(按表头字段)
    for d in data:
        info = [d[0].strftime('%Y-%m-%d %H:%M:%S'), d[1], d[2], d[3], d[4], d[5]]
        temp = dict(zip(title, info))
        fina.append(temp)
    # 将服务器的分配cpu，内存，实例cpu，内存等信息组合
    instance_allocate = ['cpu_allocate', 'cpu_instance', 'memory_allocate', 'memory_instance', 'flow_allocate',
                         'flow_instance']
    server_config = []
    allocate = Pattern.objects.get(pattern=pattern_ip.pattern)
    # # 该服务器所在实例的实例类型
    instance_type = InsType.objects.get(ip=pattern_ip.ip).ins_type
    # 利用正则表达式将实例配置的数字取出来
    instance_type = re.findall(r"\d+\.?\d*", instance_type)
    one_server_config = [allocate.cpu_num, instance_type[0], allocate.memory_num, instance_type[1],
                         allocate.flow_num, instance_type[2]]
    temp = dict(zip(instance_allocate, one_server_config))
    server_config.append(temp)
    return render(request, 'break_log.html', {'break_data': json.dumps(fina), 'server_config': server_config})


def server_search(request):
    # 获取网页数据
    detail_server_name = cache.get('detail_server_name')
    start = request.POST['start']
    end = request.POST['end']
    time_start = request.POST['time_start']
    time_end = request.POST['time_end']
    if len(time_end) == 0:
        time_end = "24:00"
    # 在崩溃数据库查询出崩溃的服务器
    # data = mysql_server_break.search(detail_server_name[0], start, end, time_start, time_end)
    data = BreakLogSearch.objects.raw("""select time,max_player,cpu,memory,send_flow,recv_flow,id from 
        zero_break_log_search where server_name='%s' and (time >= '%s' or '%s'='') and (time <='%s' or '%s'='') 
        and (hour(time)>='%s' or '%s'='') and (hour(time)<'%s' or '%s'='');""" %
                                      (detail_server_name[0], start, start, end, end, time_start, time_start, time_end,
                                       time_end))
    pattern_ip = ServerListUpdate.objects.get(server_name=detail_server_name[0])

    # 表头信息
    title = ["time", "player", "CPU", "memory", "send_flow", "recv_flow"]
    fina = []
    # 组json字符串(按表头字段)
    for d in data:
        info = [d.time.strftime('%Y-%m-%d %H:%M:%S'), d.max_player, d.cpu, d.memory, d.send_flow, d.recv_flow]
        temp = dict(zip(title, info))
        fina.append(temp)
    # 将服务器的分配cpu，内存，实例cpu，内存等信息组合
    instance_allocate = ['cpu_allocate', 'cpu_instance', 'memory_allocate', 'memory_instance', 'flow_allocate',
                         'flow_instance']
    server_config = []
    allocate = Pattern.objects.get(pattern=pattern_ip.pattern)
    # # 该服务器所在实例的实例类型
    instance_type = InsType.objects.get(ip=pattern_ip.ip).ins_type
    # 利用正则表达式将实例配置的数字取出来
    instance_type = re.findall(r"\d+\.?\d*", instance_type)
    one_server_config = [allocate.cpu_num, instance_type[0], allocate.memory_num, instance_type[1],
                         allocate.flow_num, instance_type[2]]
    temp = dict(zip(instance_allocate, one_server_config))
    server_config.append(temp)
    r = HttpResponse(json.dumps({'fina': fina, 'server_config': server_config}))
    return r


# 服务器详情-基本信息
def server_info(request):
    # detail_server_name是一个列表list
    detail_server_name = cache.get('detail_server_name')
    # 数据库查询
    # data = ServerListUpdate.objects.get(server_name=detail_server_name[0])
    rule_id = ServerNameRule.objects.get(server_name=detail_server_name[0]).id
    redis_conn = get_redis_connection('default')
    data = redis_conn.hmget('server:%d' % rule_id, 'account', 'instance_id')
    instance_id = data[1].decode('utf-8')
    account = data[0].decode('utf-8')
    return render(request, 'server_info.html', {'instance': instance_id, 'account': account})


# 服务器详情-数据分析
def data_analyse(request):
    detail_server_name = cache.get('detail_server_name')
    # 调用数据模块获取数据
    series, max_player, cpu_allocate, cpu_instance, memory_allocate, memory_instance, flow_allocate, flow_instance, \
        time_line = data_count.day_count(day=7, tyflag=-2, start='', dur=0, server=detail_server_name)

    return render(request, 'data_analyse.html', {'time_line': time_line, 'series': series, 'max_player': max_player,
                                                 'cpu_allocate': cpu_allocate, 'cpu_instance': cpu_instance,
                                                 'memory_allocate': memory_allocate,
                                                 'memory_instance': memory_instance,
                                                 'flow_allocate': flow_allocate, 'flow_instance': flow_instance})


def command_one(request):
    # 获取命令
    command = request.POST['send_command']
    server_name = request.POST['server_name']
    cache.set('command', command)
    # 获取ip地址
    data = ServerListUpdate.objects.get(server_name=server_name)
    # 发送命令
    send_command_one.send(server_name, data.ip, data.user, command)

    return HttpResponse('发送成功')


def look_command_log(request):
    detail_server_name = cache.get('detail_server_name')
    command_data = CommandLog.objects.filter(server_name=detail_server_name[0]).values_list('server_name',
                                                                                    'send_command', 'time')
    # 表头信息
    title = ["time", "server_name", "command"]
    fina = []

    for t in command_data:
        one_command_info = [t[2].strftime('%Y-%m-%d %H:%M:%S'), t[0], t[1]]
        temp = dict(zip(title, one_command_info))
        fina.append(temp)
    return render(request, 'look_command_log.html', {'data': fina})


# 发送命令
def send_command(request):
    detail_server_name = cache.get('detail_server_name')
    # 获取ip地址，该实例所属账户,实例名称
    data = ServerListUpdate.objects.get(server_name=detail_server_name[0])
    # 获取该实例下所有的服务器名称
    # cpu = server_info_name.servername(data.ip, data.user)
    return render(request, 'send_command.html', {"user": data.account, "instance": data.instance_id,
                                                 "server": detail_server_name[0]})


# 更新
def update(request):
    # 获得要更新到的版本号和将要更新的服务器
    select_update_version = request.POST['select_update_version']
    select_update_server = request.POST['select_update_server']
    # 将json字符串变成列表
    select_update_server = json.loads(select_update_server)
    # 选择的服务器
    for se_ser in select_update_server:
        # 根据选中的服务器名称获取服务器的文件名uuid和进程号,ip地址和用户
        filename_uuid = Version.objects.get(server_name=se_ser['server_name']).filename_uuid
        pid = ServerPid.objects.get(server_name=se_ser['server_name']).pid
        info = ServerListUpdate.objects.get(server_name=se_ser['server_name'])
        ip = info.ip
        user = info.user
        pattern = info.pattern
        zone = info.zone
        run_company = info.run_company
        # print(filename_uuid, pid, ip, user, pattern, zone, run_company)
        # 退出该进程并且删除服务器文件，并且清除该服务器的zero_server_pid,zero_version,zero_server_list_update表
        update_kill_old.kill(ip, user, filename_uuid, pid, se_ser['server_name'])

        # 根据选中的版本查找对应的文件名
        filename = AddVersion.objects.get(version=select_update_version).version

        # 将要更新的版本拷贝至相应实例存放服务器的文件夹下,开服务器并将新服务器记录插入数据表中
        new_uid = update_server.update_server(ip, user, filename, select_update_version, pattern, zone,
                                              run_company, se_ser['server_name'])
        # 休眠1秒，待服务器完全开启后，将cpu,memory等信息插入到服务器最新表zero_server_list_update中
        time.sleep(1)
        insert_server_update.insert_mysql(ip, user, new_uid)
    return HttpResponse(json.dumps('更新完毕'))


# 迁移
def move(request):
    select_migrate_server = request.POST['select_migrate_server']
    select_migrate_pattern = request.POST['select_migrate_pattern']
    # print(select_migrate_server, select_migrate_pattern)
    select_migrate_server = json.loads(select_migrate_server)
    for se_mi in select_migrate_server:
        # migrate_server_pattern.migrate(se_mi['server_name'], select_migrate_pattern)
        ServerListUpdate.objects.filter(server_name=se_mi['server_name']).update(pattern=select_migrate_pattern)
        # zero_server_list_update中搜寻要迁移的服务器的源ip和源user
        ip_user = ServerListUpdate.objects.get(server_name=se_mi['server_name'])
        ori_ip = ip_user.ip
        ori_user = ip_user.user
        # 搜寻该服务器的pid和filename_uuid等,zero_server_pid,
        # ori_pid = ServerPid.objects.get(cpu=se_mi['cpu']).pid
        ori_info = Version.objects.get(server_name=se_mi['server_name'])
        ori_filename_uuid = ori_info.filename_uuid
        ori_filename = ori_info.version
        ori_version = ori_info.version
        ori_zone = ori_info.zone
        ori_run_company = ori_info.run_company

        # server_list_update中搜寻有要迁移的模式的所有的目的ip和目的user,列表
        dest_ip = [x[0] for x in ServerListUpdate.objects.filter(pattern=select_migrate_pattern).values_list('ip')]
        dest_user = [x[0] for x in ServerListUpdate.objects.filter(pattern=select_migrate_pattern).values_list('user')]
        # 遍历有要迁移的模式的ip和user，如果和源ip和目的ip一样，则判断该模式是否还能放进服务器，能则开服
        for i in range(len(dest_ip)):
            if dest_ip[i] == ori_ip:
                # 判断能否开启服务器，能
                status = batch_add_memory.search(dest_ip, select_migrate_pattern)
                # 迁移后少一个位置
                status = status + 1
                if status:
                    # 关闭服务器，删除zero_server_pid  zero_version表中相应的数据,并将
                    # quit_server.quit_server(ori_ip, ori_user, ori_filename_uuid)
                    # ServerPid.objects.filter(server_name=se_mi['server_name']).delete()
                    # Version.objects.filter(server_name=se_mi['server_name']).delete()
                    # delete_table_one.delete(se_mi['cpu'])
                    # 按迁移的服务器模式开启服务器，并将数据插入相应的数据表,flag=0表示不需要拷贝至其他实例
                    start_server.start(0, ori_ip, ori_user, dest_ip[i], dest_user[i], ori_filename, ori_version,
                                       select_migrate_pattern, ori_zone, ori_run_company, ori_filename_uuid,
                                       se_mi['server_name'])
                    # break出循环外
                    break
            # 源ip不能放入服务器，则在其他有该模式的实例上迁移服务器。
            # 判断能否放下服务器，能
            status = batch_add_memory.search(dest_ip, select_migrate_pattern)
            if status:
                # 关闭服务器，删除zero_server_pid  zero_version表中相应的数据
                quit_server.quit_server(ori_ip, ori_user, ori_filename_uuid)
                # ServerPid.objects.filter(server_name=se_mi['server_name']).delete()
                # Version.objects.filter(server_name=se_mi['server_name']).delete()
                # delete_table_one.delete(se_mi['server_name'])
                # 按迁移的服务器模式开启服务器，并将数据插入相应的数据表
                start_server.start(1, ori_ip, ori_user, dest_ip[i], dest_user[i], ori_filename, ori_version,
                                   select_migrate_pattern, ori_zone, ori_run_company, ori_filename_uuid,
                                   se_mi['server_name'])
                # break出循环外
                break
    return HttpResponse(json.dumps('bingo'))


# class BatchAddView(View):
#     """批量新增服务器"""
#     # 初始化
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.database_version = [x[0] for x in AddVersion.objects.values_list('version')]
#         self.database_pattern = [x[0] for x in Pattern.objects.values_list('pattern')]
#         self.database_run_company = [x[0] for x in RunCompany.objects.values_list('run_company_name')]
#         self.database_zone = [x[0] for x in ServerAccountZone.objects.values_list('zone').distinct()]
#
#     # get请求
#     def get(self, request):
#         return render(request, 'batch_add.html',
#                       {'show_version': self.database_version, 'show_pattern': self.database_pattern,
#                        'show_run_company': self.database_run_company, 'show_zone': self.database_zone})
#
#     # post请求
#     def post(self, request):
#         # 前端页面获取新增服务器信息
#         add_num = request.POST['add_num']
#         select_pattern = request.POST['select_pattern']
#         select_version = request.POST['select_version']
#         select_zone = request.POST['select_zone']
#         select_run_company = request.POST['select_run_company']
#
#         # 要开设的服务器版本所对应的文件名
#         filename = AddVersion.objects.get(version=select_version).filename
#
#         # 要新增的服务器个数
#         total = int(add_num)
#         # 根据模式搜寻该模式的实例类型
#         ins_type = Pattern.objects.get(pattern=select_pattern).ins_type
#
#         # 获取最大带宽和磁盘大小
#         disksize = ins_type.split('/')[2].replace('G', '')
#         width = ins_type.split('/')[3].replace('Mbps', '')
#
#         # 根据账户表查看所有账户下所有实例的类型，符合所要开服的模式，就记录ip.
#         ip = real_time_account_ip.ip(ins_type)
#         # 根据实例类型获得ip地址和所属账户
#         ip_account = InsType.objects.filter(ins_type=ins_type).values_list('ip', 'account_name')
#
#         # ip = []
#         account = []
#         # 根据ip所属账户查看该账户是否在云账户列表新增实例页面添加购买过所选择的地区，从而过滤出能够新增服务器的ip地址
#
#         for data in ip_account:
#             res = ServerAccountZone.objects.filter(account_name=data[1]).values_list('zone')
#             if select_zone in [x[0] for x in res]:
#                 # ip = (data[0])
#                 account = (data[1])
#         # 账户去重
#         account = list(set(account))
#         account_id = []
#         account_key = []
#         for acc in account:
#             id_temp = Account.objects.get(account_name=acc).account_id
#             key_temp = Account.objects.get(account_name=acc).account_key
#             account_id = (id_temp)
#             account_key = (key_temp)
#         # 检查该实例下分配给该模式的空间还够开几个服务器
#         for i in ip:
#             status = batch_add_memory.search(i, select_pattern)
#             if status == 0:
#                 continue
#             elif status >= total:
#                 for j in range(total):
#                     uid = batch_add_start_server.add_server(i, 'root', filename, select_version, select_pattern,
#                                                             select_zone, select_run_company)
#                     # 休眠，让程序完全启动
#                     time.sleep(5)
#                     insert_server_update.insert_mysql(i, 'root', uid)
#                     # 已经开启一个服务器
#                     total -= 1
#                 break
#             elif status < total:
#                 for k in range(status):
#                     uid = batch_add_start_server.add_server(i, 'root', filename, select_version, select_pattern,
#                                                             select_zone, select_run_company)
#                     # 休眠，让程序完全启动
#                     time.sleep(5)
#                     insert_server_update.insert_mysql(i, 'root', uid)
#                 total -= status
#         # 如果遍历完所有可用实例依然没有达到新增服务器的数量，就购买实例
#         # 按照新增服务器模式配置购买此类型实例,遍历账户购买实例
#         flag = 0
#         for i in range(len(account_id)):
#             if total > 0:
#                 # 根据区域查询实例机型,zone代码，实例机型
#                 cpu = ins_type.split('/')[0].replace('核', '')
#                 memory = ins_type.split('/')[1].replace('G', '')
#                 zone, instype = buy_search_instype.search(account_id[i], account_key[i], select_zone, cpu, memory)
#                 # 根据所选择地域，模式的付费类型，zone代码，实例类型，磁盘大小，按照计费模式计算价格
#                 price = []
#                 region = []
#                 zone_code = []
#                 instype_list = []
#                 imageid = []
#                 pay_type = []
#                 for j in range(0, len(zone)):
#                     price_temp, region_temp, zone_tmep, instype_temp, imageid_temp, pay_type_temp, disksize_temp \
#                         = buy_inquery_price.inquery(account_id[i], account_key[i], select_pattern, select_zone,
#                         zone[j], instype[j])
#                     price = (price_temp)
#                     region = (region_temp)
#                     zone_code = (zone_tmep)
#                     instype_list = (instype_temp)
#                     imageid = (imageid_temp)
#                     pay_type = (pay_type_temp)
#                 # 根据价格最低购买实例。(获取下标，获取各列表同样下标位置。从而购买该配置的实例)
#                 min_price_index = price.index(min(price))
#                 buy_ins.buy(account_id[i], account_key[i], region[min_price_index], pay_type[min_price_index],
#                            zone[min_price_index], instype[min_price_index], imageid[min_price_index], disksize, width)
#                 # 实例创建完毕后,检测状态,如果为运行状态后,进行后续操作
#                 ip = monitor_ins_status.monitor(account_id, account_key, region[min_price_index])
#                 if ip != 0:
#                     # 建立文件夹,安装相关软件及设置定时任务的操作。
#                     install_and_mkdir.install(ip, 'root')
#                     flag = 1
#                 # 判断该实例是否满足剩余开通服务器的个数，满足则退出循环，不再购买，不满足则用另一个账户继续购买。
#                 size = Pattern.objects.get(pattern=select_pattern).memory_num
#                 if int(disksize) / int(size) >= total:
#                     break
#
#         if flag == 1:
#             return HttpResponse(json.dumps('已购买实例，请等待实例创建完毕运行后再新增服务器'))
#         return HttpResponse(json.dumps('bingo'))


# 批量新增
def batch_add(request):
    # 在数据库中将全部版本，模式，运营商搜出来返回给前端页面以供选择
    database_version = [x[0] for x in AddVersion.objects.values_list('version')]
    database_pattern = [x[0] for x in Pattern.objects.values_list('pattern')]
    database_run_company = [x[0] for x in RunCompany.objects.values_list('run_company_name')]
    database_zone = [x[0] for x in ServerAccountZone.objects.values_list('zone').distinct()]
    return render(request, 'batch_add.html',
                  {'show_version': database_version, 'show_pattern': database_pattern,
                   'show_run_company': database_run_company, 'show_zone': database_zone})


# 新增服务器
def add_server(request):
    # 前端页面获取新增服务器信息
    add_num = request.POST['add_num']
    select_pattern = request.POST['select_pattern']
    select_version = request.POST['select_version']
    select_zone = request.POST['select_zone']
    select_run_company = request.POST['select_run_company']

    # 要开设的服务器版本所对应的文件名
    filename = AddVersion.objects.get(version=select_version).version

    # 要新增的服务器个数
    total = int(add_num)
    # 根据模式搜寻该模式的实例类型
    ins_type = Pattern.objects.get(pattern=select_pattern).ins_type
    # 根据模式搜寻该模式允许的最大在线人数
    player_num = Pattern.objects.get(pattern=select_pattern).player_num
    # 获取最大带宽和磁盘大小
    disk_size = ins_type.split('/')[3].replace('G', '')
    width = ins_type.split('/')[2].replace('Mbps', '')

    # 根据账户表查看所有账户下所有实例的类型，符合所要开服的模式，就记录ip.
    ip = real_time_account_ip.ip(ins_type)
    # 根据实例类型获得ip地址和所属账户
    ip_account = InsType.objects.filter(ins_type=ins_type).values_list('ip', 'account_name')

    # ip = []
    account = []
    # 根据ip所属账户查看该账户是否在云账户列表新增实例页面添加购买过所选择的地区，从而过滤出能够新增服务器的ip地址

    for data in ip_account:
        res = ServerAccountZone.objects.filter(account_name=data[1]).values_list('zone')
        if select_zone in [x[0] for x in res]:
            # ip.append(data[0])
            account.append(data[1])
    # 账户去重
    account = list(set(account))
    account_id = []
    account_key = []
    for acc in account:
        id_temp = Account.objects.get(account_name=acc).account_id
        key_temp = Account.objects.get(account_name=acc).account_key
        account_id.append(id_temp)
        account_key.append(key_temp)
    # 检查该实例下分配给该模式的空间还够开几个服务器
    for i in ip:
        status = batch_add_memory.search(i, select_pattern)
        if status <= 0:
            continue
        elif status >= total:
            for j in range(total):
                uid = batch_add_start_server.add_server(i, 'root', filename, select_version, select_pattern,
                                                        select_zone, select_run_company, player_num)
                # 休眠，让程序完全启动
                time.sleep(1)
                insert_server_update.insert_mysql(i, 'root', uid)
                # 已经开启一个服务器
                total -= 1
            break
        elif status < total:
            for k in range(status):
                uid = batch_add_start_server.add_server(i, 'root', filename, select_version, select_pattern,
                                                        select_zone, select_run_company, player_num)
                # 休眠，让程序完全启动
                time.sleep(1)
                insert_server_update.insert_mysql(i, 'root', uid)
            total -= status
    # 如果遍历完所有可用实例依然没有达到新增服务器的数量，就购买实例
    # 按照新增服务器模式配置购买此类型实例,遍历账户购买实例
    flag = 0
    for i in range(len(account_id)):
        if total > 0:
            # 根据区域查询实例机型,zone代码，实例机型
            cpu = ins_type.split('/')[0].replace('核', '')
            memory = ins_type.split('/')[1].replace('G', '')
            zone, instype = buy_search_instype.search(account_id[i], account_key[i], select_zone, cpu, memory)
            # 根据所选择地域，模式的付费类型，zone代码，实例类型，磁盘大小，按照计费模式计算价格
            price = []
            region = []
            zone_code = []
            ins_type_list = []
            image_id = []
            pay_type = []
            for j in range(0, len(zone)):
                price_temp, region_temp, zone_temp, ins_type_temp, image_id_temp, pay_type_temp, disk_size_temp \
                    = buy_inquery_price.inquery(account_id[i], account_key[i], select_pattern, select_zone, zone[j],
                                                instype[j])
                price.append(price_temp)
                region.append(region_temp)
                zone_code.append(zone_temp)
                ins_type_list.append(ins_type_temp)
                image_id.append(image_id_temp)
                pay_type.append(pay_type_temp)
            # 根据价格最低购买实例。(获取下标，获取各列表同样下标位置。从而购买该配置的实例)
            min_price_index = price.index(min(price))
            # print(min_price_index, price[min_price_index])
            buy_ins.buy(account_id[i], account_key[i], region[min_price_index], pay_type[min_price_index],
                        zone[min_price_index], instype[min_price_index], image_id[min_price_index], disk_size, width)
            # 实例创建完毕后,检测状态,如果为运行状态后,进行后续操作,ip是列表
            ip = monitor_ins_status.monitor(account_id[i], account_key[i], region[min_price_index])
            if ip[0] != 0:
                # 建立文件夹,安装相关软件及设置定时任务的操作。
                install_and_mkdir.install(ip[0], 'root')
                flag = 1
            # 判断该实例是否满足剩余开通服务器的个数，满足则退出循环，不再购买，不满足则用另一个账户继续购买。
            size = Pattern.objects.get(pattern=select_pattern).disk_num
            if int(disk_size) / int(size) >= total:
                break

    if flag == 1:
        return HttpResponse(json.dumps('已购买实例,还需新增%d个服务器，请手动新增服务器' % total))
    return HttpResponse(json.dumps('服务器新增完毕'))


# 批量开服
def batch_start(request):
    select_start_server = json.loads(request.POST['select_start_server'])
    # 根据服务器名称查询进程pid
    for server in select_start_server:
        data = ServerPid.objects.get(server_name=server['server_name'])
        pid = data.pid
        ip = data.ip
        user = data.user
        # 开启服务器，
        open_server.open_server(ip, user, server['server_name'], pid)

    status = mysql_server_status.search('', '', '', '', '')

    # 表头信息
    title = ["server_name", "player", "CPU", "memory", "send_flow", "recv_flow", "version", "is_activate"]
    # 返回页面的字典数据
    fina = []
    # 组json字符串(按表头字段),
    for st in status:
        one_server_info = [st.server_name, st.max_player, st.cpu, st.memory, st.send_flow, st.recv_flow, st.version, st.is_activate]
        temp = dict(zip(title, one_server_info))
        fina.append(temp)
    return HttpResponse(json.dumps(fina))


# 批量关服
def batch_quit(request):
    select_quit_server = json.loads(request.POST['select_quit_server'])
    # 根据服务器名称查询服务器文件名称uuid,退出进程，关闭服务器
    for server in select_quit_server:
        ip_user = ServerPid.objects.get(server_name=server['server_name'])
        uuid = Version.objects.get(server_name=server['server_name'])
        # pid, ip, user = search_quit_pid.search(server['server_name'])
        # 退出服务器
        # print(ip_user.ip, ip_user.user)
        quit_server.quit_server(ip_user.ip, ip_user.user, uuid.filename_uuid)
        # 更新zero_server_list_update表中is_activate状态为0，表示服务器处于关闭状态
        # update_quit_server_status.update(server['server_name'])
        data = ServerListUpdate.objects.get(server_name=server['server_name']).max_player
        max_player = '0/' + data.split('/')[-1]
        cpu = 0.0
        memory = 0.0
        send_flow = 0
        recv_flow = 0
        ServerListUpdate.objects.filter(server_name=server['server_name']).update(max_player=max_player, cpu=cpu,
                                                                                  memory=memory, send_flow=send_flow,
                                                                                  recv_flow=recv_flow, is_activate=0)
    status = mysql_server_status.search('', '', '', '', '')
    # 表头信息
    title = ["server_name", "player", "CPU", "memory", "send_flow", "recv_flow", "version", "is_activate"]
    # 返回页面的字典数据
    fina = []
    # 组json字符串(按表头字段)
    for st in status:
        one_server_info = [st.server_name, st.max_player, st.cpu, st.memory, st.send_flow, st.recv_flow, st.version, st.is_activate]
        temp = dict(zip(title, one_server_info))
        fina.append(temp)
    return HttpResponse(json.dumps(fina))


# 备份崩溃日志的时间
def log(request):
    get_time = request.POST['time']
    cache.set('get_time', get_time)
    return HttpResponse('bingo')


# 下载日志
# noinspection PyUnusedLocal
def download_log(request):
    detail_server_name = cache.get('detail_server_name')
    get_time = cache.get('get_time')
    down_name = detail_server_name[0].replace('(', '_').replace(')', '') + '_' + get_time.replace(' ', '_') + '.log'
    # down_name = detail_server_name[0].replace('(', '_').replace(')', '') + '.log'
    filename = '/home/log/%s' % down_name

    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    response = StreamingHttpResponse(file_iterator(filename))
    response['Content-Type'] = 'application/octet-stream'
    # 下载时能够有中文路径
    response['Content-Disposition'] = 'attachment;filename={0}'.format(down_name.encode('utf-8').decode('ISO-8859-1'))
    return response


# 历次更新服务器日志
def download_update_log(request):
    detail_server_name = cache.get('detail_server_name')
    # command_data = CommandLog.objects.filter(cpu=detail_server_name[0]).values_list('cpu',
    #                                                                                         'send_command', 'time')
    # 扫描/home/log文件夹，找出该服务器的更新日志，cpu_update_time.log
    # 服务器名称去掉特殊字符,格式化组装
    detail_server_name = detail_server_name[0].replace("(", "_").replace(")", "") + "_update"
    search_cmd = "ls -ltr /home/log | grep %s | awk '{print $9}'" % detail_server_name
    temp = os.popen(search_cmd)
    update_time = temp.read().strip().split("\n")

    # 表头信息
    title = ["time"]
    fina = []

    for t in update_time:
        # 没有日志的情况
        if t == '':
            continue
        one_time_info = [t.split('_')[4] + " " + t.split('_')[5].replace('.log', '')]
        temp = dict(zip(title, one_time_info))
        fina.append(temp)
    return render(request, 'download_update_log.html', {'data': fina})


# 下载更新日志的时间
def download_update_time(request):
    update_time = request.POST['time']
    cache.set('update_time', update_time)
    return HttpResponse('bingo')


# 服务器详情-基本信息页面下载日志
# noinspection PyUnusedLocal
def update_server_log(request):
    detail_server_name = cache.get('detail_server_name')
    update_time = cache.get('update_time')
    down_name = detail_server_name[0].replace('(', '_').replace(')', '') + '_update_' + \
        update_time.replace(' ', '_') + '.log'
    # 根据选中的服务器查找到文件名(uuid),ip地址和user用户
    # uuid = Version.objects.get(cpu=detail_server_name[0]).filename_uuid
    # ip_user = ServerListUpdate.objects.get(cpu=detail_server_name[0])
    # ip = ip_user.ip
    # user = ip_user.user
    # # uuid, ip, user = search_filename_uuid.search(detail_server_name[0])
    # # 进入服务器文件将nohup.out文件拷贝到本实例/home/log上以供下载
    # down_cmd = "scp %s@%s:/home/server/%s/nohup.out /home/log/%s" % (user, ip, uuid, down_name)
    # os.system(down_cmd)
    # 在本地log文件夹内获取日志文件
    # print(down_name)
    filename = '/home/log/%s' % down_name

    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    response = StreamingHttpResponse(file_iterator(filename))
    response['Content-Type'] = 'application/octet-stream'
    # 下载时能够有中文路径
    response['Content-Disposition'] = 'attachment;filename={0}'.format(down_name.encode('utf-8').decode('ISO-8859-1'))

    return response


# 服务器详情-基本信息页面下载日志
# noinspection PyUnusedLocal
def info_log(request):
    detail_server_name = cache.get('detail_server_name')
    down_name = detail_server_name[0].replace('(', '_').replace(')', '') + '.log'
    # 根据选中的服务器查找到文件名(uuid),ip地址和user用户
    uuid = Version.objects.get(server_name=detail_server_name[0]).filename_uuid
    ip_user = ServerListUpdate.objects.get(server_name=detail_server_name[0])
    ip = ip_user.ip
    user = ip_user.user
    # uuid, ip, user = search_filename_uuid.search(detail_server_name[0])
    # 进入服务器文件将nohup.out文件拷贝到本实例/home/log上以供下载
    down_cmd = "scp %s@%s:/home/server/%s/nohup.out /home/log/%s" % (user, ip, uuid, down_name)
    os.system(down_cmd)
    # 在本地log文件夹内获取日志文件
    filename = '/home/log/%s' % down_name

    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    response = StreamingHttpResponse(file_iterator(filename))
    response['Content-Type'] = 'application/octet-stream'
    # 下载时能够有中文路径
    response['Content-Disposition'] = 'attachment;filename={0}'.format(down_name.encode('utf-8').decode('ISO-8859-1'))

    return response
