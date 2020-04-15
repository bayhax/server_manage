from django.urls import path
from apps.server_list import views

urlpatterns = [
    # re_path(r'server', views.index),  # 服务器
    path('index', views.index),  # 服务器列表
    path('refresh', views.refresh),  # 刷新按钮
    path('search', views.search),  # 查询按钮
    path('select', views.select),  # 选择
    path('statistics', views.statistics),  # 统计按钮
    # re_path(r'statistics_show',views.statistics_show),
    path('info_log', views.info_log),  # 服务器基本信息页面下载日志
    path('break_log', views.break_log),  # 服务器详情崩溃日志页面
    path('server_log', views.server_log),
    path('server_info', views.server_info),  # 服务器详情基本信息页面
    path('data_analysize', views.data_analysize),  # 服务器详情-数据分析
    path('send_command', views.send_command),  # 发送命令
    path('command_one', views.command_one),  # 命令单个
    # path('command_all', views.command_all),  # 命令全部
    # path('start_all', views.start_all),  # 全部启动
    # path('close_all', views.close_all),  # 全部关闭
    path('look_command_log', views.look_command_log),  # 查看命令
    path('download_log', views.download_log),  # 下载日志
    path('data_analysize', views.data_analysize),  # 服务器详情数据分析页面
    # re_path(r'select_version',views.select_version),  # 选择配置版本的服务器
    path('config_pattern', views.config_pattern),  # 模式配置
    path('config_version', views.config_version),  # 版本配置
    path('update', views.update),  # 更新按钮
    path('move', views.move),  # 迁移
    path('batch_add', views.batch_add),  # 批量新增
    path('add_server', views.add_server),  # 新增服务器
    path('batch_quit', views.batch_quit),  # 批量关服
    path('batch_start', views.batch_start),  # 批量开服
    # path('five_span', views.five_span),  # 五分钟细粒度
    path('during_date_count', views.during_date_count),  # 时间段
    path('during_date_tendency', views.during_date_tendency),
    path('today_count', views.today_count),  # 今日统计
    path('today_tendency', views.today_tendency),  # 今日趋势
    path('yesterday_count', views.yesterday_count),  # 昨日统计
    path('yesterday_tendency', views.yesterday_tendency),  # 昨日趋势
    path('seven_count', views.seven_count),  # 近7日统计
    path('seven_tendency', views.seven_tendency),  # 近七日趋势
    path('thirty_count', views.thirty_count),  # 近30日统计
    path('thirty_tendency', views.thirty_tendency),  # 近30日趋势
    path('detail_during_date_count', views.detail_during_date_count),  # 时间段
    path('detail_during_date_tendency', views.detail_during_date_tendency),
    path('detail_today_count', views.detail_today_count),  # 今日统计
    path('detail_today_tendency', views.detail_today_tendency),  # 今日趋势
    path('detail_yesterday_count', views.detail_yesterday_count),  # 昨日统计
    path('detail_yesterday_tendency', views.detail_yesterday_tendency),  # 昨日趋势
    path('detail_seven_count', views.detail_seven_count),  # 近7日统计
    path('detail_seven_tendency', views.detail_seven_tendency),  # 近七日趋势
    path('detail_thirty_count', views.detail_thirty_count),  # 近30日统计
    path('detail_thirty_tendency', views.detail_thirty_tendency),  # 近30日趋势
    path('download_update_log', views.download_update_log),  # 历次更新日志的时间
    path('update_server_log', views.update_server_log),  # 下载服务器更新日志
    path('download_update_time', views.download_update_time),  # 更新服务器的时间
    path('log', views.log),  # 日志时间
    path('download_log', views.download_log),  # 下载日志
    path('server_search', views.server_search),  # 查询时间段下载崩溃日志
]
