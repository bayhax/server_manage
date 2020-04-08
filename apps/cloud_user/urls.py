from django.urls import path, re_path
from apps.cloud_user import views
urlpatterns = [
    re_path(r'cloud_user', views.cloud_user),  # 服务器
    path('upload', views.upload),  # 上传账户信息
    path('save_info', views.save_info),  # 保存账户信息入库
    path('save_account_zone', views.save_account_zone),  # 入库账户可用区
]
