from django.urls import path
from apps.server_list import views

urlpatterns = [
    path('index', views.index),  # 服务器列表
    path('refresh', views.refresh),  # 刷新按钮
    path('search', views.search),  # 查询按钮
    path('select', views.select),  # 选择
    path('statistics', views.statistics),  # 统计按钮
    path('info_log', views.info_log),  # 服务器基本信息页面下载日志
    path('break_log', views.break_log),  # 服务器详情崩溃日志页面
    path('server_log', views.server_log),
    path('server_info', views.server_info),  # 服务器详情基本信息页面
    path('send_command', views.send_command),  # 发送命令
    path('command_one', views.command_one),  # 命令单个
    path('look_command_log', views.look_command_log),  # 查看命令
    path('download_log', views.download_log),  # 下载日志
    path('data_analyse', views.data_analyse),  # 服务器详情数据分析页面
    path('update', views.update),  # 更新按钮
    path('move', views.move),  # 迁移
    path('batch_add', views.batch_add),  # 批量新增
    path('add_server', views.add_server),  # 新增服务器
    path('batch_quit', views.batch_quit),  # 批量关服
    path('batch_start', views.batch_start),  # 批量开服
    # path('statistics_count', views.statistics_count),  # 统计
    path('statistics_count', views.CountView.as_view()),  # 统计
    path('statistics_tendency', views.TendencyView.as_view()),  # 趋势
    # path('detail_count', views.detail_count),  # 服务器详情统计
    path('detail_count', views.DetailCountView.as_view()),  # 服务器详情统计
    path('detail_tendency', views.DetailTendencyView.as_view()),  # 服务器详情趋势
    path('download_update_log', views.download_update_log),  # 历次更新日志的时间
    path('update_server_log', views.update_server_log),  # 下载服务器更新日志
    path('download_update_time', views.download_update_time),  # 更新服务器的时间
    path('log', views.log),  # 日志时间
    path('download_log', views.download_log),  # 下载日志
    path('server_search', views.server_search),  # 查询时间段下载崩溃日志
]
