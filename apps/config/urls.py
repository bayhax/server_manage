from django.urls import path, include, re_path
from config import views
urlpatterns = [
    path('config_pattern',views.config_pattern),  # 模式配置
    path('config_version',views.config_version),  # 版本配置
    path('config_run_company',views.config_run_company),  # 服务器配置
    #path('select_version',views.select_version),  # 选择的服务器
    path('get_version_name',views.get_version_name),  # 获取版本名称
    path('config_version_edit',views.config_version_edit),  # 版本编辑
    path('config_add_version',views.config_add_version),  # 版本添加
    path('version_confirm_edit',views.version_confirm_edit),  # 版本编辑确认
    path('version_delete',views.version_delete),  # 版本删除
    path('config_add_version_confirm',views.config_add_version_confirm),  # 版本添加库
    path('config_add_pattern',views.config_add_pattern),  # 模式添加
    path('config_pattern_edit',views.config_pattern_edit),  # 模式编辑  
    path('confirm_edit',views.confirm_edit),  # 模式编辑页面确认
    path('get_pattern_name',views.get_pattern_name),  # 模式名称获取
    path('config_add_pattern_confirm',views.config_add_pattern_confirm), #模式添加存库
    path('pattern_delete',views.pattern_delete),  # 删除模式
    path('config_add_run_company',views.config_add_run_company),  # 运营商添加
    path('config_add_run_company_confirm',views.config_add_run_company_confirm),  # 运营商添加存库
    path('get_run_company_name', views.get_run_company_name),  # 获取运营商名称
    path('run_company_delete',views.run_company_delete),  # 运营商删除
    path('run_company_confirm_edit',views.run_company_confirm_edit),  # 运营商编辑页面确认
    path('config_run_company_edit', views.config_run_company_edit),  # 运营商编辑
    path('config_plat', views.config_plat),  # 平台配置
    path('config_add_plat', views.config_add_plat),  # 平台添加
    path('config_add_plat', views.config_add_plat),  # 平台添加
    path('config_add_plat_confirm', views.config_add_plat_confirm),  # 平台存库
    path('plat_confirm_edit', views.plat_confirm_edit),  # 平台编辑页面确认
    path('config_plat_edit', views.config_plat_edit),  # 平台编辑
    path('get_plat_name', views.get_plat_name),  # 平台名称获取
    path('plat_delete', views.plat_delete),  # 平台删除
    path('upload', views.upload),  # 上传文件
]

