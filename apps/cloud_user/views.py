from django.shortcuts import HttpResponse
from django.shortcuts import render
import json

from cloud_user import insert_account_zone
from cloud_user.models import Account, ServerAccountZone, AccountZone


# http://127.0.0.1:8000
# 云账户列表
def cloud_user(request):
    account_list = []  # 账户列表
    temp1 = []
    data = {}  # 传给前端的字典数据，账户和可用区相对应
    # 连接腾讯云，获取最新信息, 速度有点慢。每五分钟更新一次
    # insert_account_zone.insert()
    # 查询出账户列表
    account_zone = AccountZone.objects.values_list('account_name', 'region')
    # 如果账户列表不等于空，即一开始还没有账户，要上传的时候
    if len(account_zone) != 0:
        # 遍历账户
        for az in account_zone:
            exist_zone = []
            account_list.append(az[0])

            # 该账户已经配置过的地区
            exist_zone_temp = ServerAccountZone.objects.filter(account_name=az[0]).values_list('zone')
            for ex in exist_zone_temp:
                exist_zone.append(ex[0])

            # 所有可用区，去掉地区名称前面的空格
            temp = [x.strip() for x in az[1].split(',')]

            # 可用没有配置过的地区，给初始化页面使用
            data[az[0]] = [x for x in temp if x not in exist_zone]

        # 页面初始显示的一行为第一个账户的可用区列表temp1
        temp1 = data[account_list[0]]

    return render(request, 'user_list.html', {'account_list': account_list, 'available_zone': temp1, 'data': data})


# 上传账户信息
def upload(request):
    return render(request, 'upload_account_info.html')


# 将账户信息存入数据库
def save_info(request):
    secu_id = request.POST['id']
    secu_key = request.POST['key']
    acc = request.POST['account']
    try:
        clou = Account(account_name=acc, account_id=secu_id, account_key=secu_key)
        # 防止重复
        clou.save(force_insert=True)
        # 每次连接腾讯云，获取最新信息, 速度有点慢。可以在新增账户时直接查询
        insert_account_zone.insert()
        return HttpResponse('账户信息入库成功')
    except Exception as e:
        print(e)
        return HttpResponse('账户信息入库失败，请检查账户是否已经存在')


# 将新增实例可用区存入数据库
def save_account_zone(request):
    try:
        # 接收前端数据变成列表
        account_list = json.loads(request.POST['account_list'])
        zone_list = json.loads(request.POST['zone_list'])
        for i in range(len(account_list)):
            insert_zone = ServerAccountZone(account_name=account_list[i], zone=zone_list[i])
            insert_zone.save(force_insert=True)
        return HttpResponse('新增地区成功')
    except Exception as e:
        print(e)
        return HttpResponse('新增失败')
