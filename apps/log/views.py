import datetime

from django.http import StreamingHttpResponse
from django.shortcuts import HttpResponse
from django.shortcuts import render
import json

from pytz import timezone

from apps.log import mysql_server_break
# from apps.log import mysql_break_log
from django.core.cache import cache
from log.models import BreakLogSearch


# 崩溃日志查询
def search_break_log(request):

    # 数据库查询结果为tuple，放进列表
    version = BreakLogSearch.objects.values_list('version', flat=True).distinct()
    zone = BreakLogSearch.objects.values_list('zone', flat=True).distinct()
    platform = BreakLogSearch.objects.values_list('plat', flat=True).distinct()
    run_company = BreakLogSearch.objects.values_list('run_company', flat=True).distinct()

    # 浏览器显示内容，instance,server为给浏览器返回的内容
    data = mysql_server_break.search('', '', '', '', '', '', '', '', '')
    title = ["riqi", "server_name"]
    fina = []
    # 组json字符串(按表头字段)
    for d in data:
        break_server = [d.time.strftime('%Y-%m-%d %H:%M:%S'), d.server_name]
        temp = dict(zip(title, break_server))
        fina.append(temp)
    return render(request, 'search_break_log.html',
                  {
                      'zone': zone,
                      'platform': platform,
                      'run_company': run_company,
                      'version': version,
                      'all_data': fina,
                  })


# 查询按钮
def server_search(request):
    # 获取网页数据
    servername = request.POST['servername']
    version = request.POST['vers']
    zone = request.POST['zos']
    plat = request.POST['plats']
    run_company = request.POST['runs']
    start = request.POST['start']
    end = request.POST['end']
    time_start = request.POST['time_start']
    time_end = request.POST['time_end']
    if len(time_end) == 0:
        time_end = "24:00"
    # 在崩溃数据库查询出崩溃的服务器
    data = mysql_server_break.search(servername, version, zone, plat, run_company, start, end, time_start, time_end)

    # 表头信息
    title = ["riqi", "server_name"]
    fina = []
    # 组json字符串(按表头字段)
    for d in data:
        break_server = [d.time.strftime('%Y-%m-%d %H:%M:%S'), d.server_name]
        temp = dict(zip(title, break_server))
        fina.append(temp)
    r = HttpResponse(json.dumps(fina))

    return r


# 得到选中的服务器名称
def get_name(request):
    server_name = request.POST['server_name']
    riqi = request.POST['riqi']
    cache.set('server_name', server_name)
    cache.set('riqi', riqi)
    return HttpResponse(server_name)


# 详情页
# def details(request):
#     server_name = cache.get('server_name')
#
#     return render(request, 'break_server_info.html', {'server_name': server_name})


# 崩溃的服务器cpu等详情页
# def break_details_search(request):
#     server_name = cache.get('server_name')
#     riqi = cache.get('riqi')
#     start = request.POST['start']
#     end = request.POST['end']
#     # 取日期的年月日
#     if len(end) == 0:
#         end = "24:00"
#     riqi = riqi[:10]
#     start = riqi + ' ' + start
#     end = riqi + ' ' + end
#     data = mysql_break_log.search(server_name, start, end)
#     # 表头信息
#     title = ["time", "player", "CPU", "memory", "send_flow", "recv_flow"]
#     fina = []
#     # 组json字符串(按表头字段)
#     for i in range(len(data)):
#         server_info = [data[i][0].strftime('%Y-%m-%d %H:%M:%S'), data[i][1], data[i][2], data[i][3],
#                        data[i][4], data[i][5]]
#         temp = dict(zip(title, server_info))
#         fina.append(temp)
#     return HttpResponse(json.dumps(fina))


# 备份崩溃日志的时间
# def log_time(request):
#     get_time = request.POST['time']
#     cache.set('get_time', get_time)
#     return HttpResponse('bingo')


# 下载崩溃日志
# noinspection PyUnusedLocal
def download_break_log(request):
    riqi = cache.get('riqi')
    server_name = cache.get('server_name').replace('(', '_').replace(')', '')
    down_name = server_name + '_' + riqi.replace(' ', '_') + '.log'
    filename = '/home/log/%s' % down_name

    def file_iterator(file_name, chunk_size=512):
        try:
            with open(file_name) as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break
        except Exception as e:
            print(e)
            print('日志文件不存在，或已销毁')

    response = StreamingHttpResponse(file_iterator(filename))
    response['Content-Type'] = 'application/octet-stream'
    # 下载时能够有中文路径
    response['Content-Disposition'] = 'attachment;filename={0}'.format(down_name.encode('utf-8').decode('ISO-8859-1'))
    return response
