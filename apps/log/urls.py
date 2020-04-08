from django.urls import path, include, re_path
from apps.log import views
urlpatterns = [
    re_path(r'search_break_log',views.search_break_log),  # 刷新按钮
    path('server_search',views.server_search),  # 按信息查询
    path('details',views.details),  # 详情页
    path('get_name',views.get_name),  # 获取服务器名称
    path('break_details_search',views.break_details_search),  # 崩溃服务器的详细信息cpu等
    path('download_break_log', views.download_break_log),  # 下载日志
    path('log_time', views.log_time),  # 崩溃日志的备份时间
]

