from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.core.cache import cache
import os
import json
from config.models import Pattern, Plat, RunCompany, AddVersion


# http://127.0.0.1:8000
# 模式配置
from server_list.models import InsType


def config_pattern(request):
    # 查询模式，数据类型为列表
    pattern = [x[0] for x in Pattern.objects.values_list('pattern')]
    title = ['pattern_name']
    # 发送给前端表格的数据
    fina = []
    # 模式名称
    for p in pattern:
        pattern_server = [p]
        temp = dict(zip(title, pattern_server))
        fina.append(temp)
    return render(request, 'config_pattern.html', {'data': json.dumps(fina)})


def get_pattern_name(request):
    pattern_name = request.POST['pattern_name']
    cache.set('pattern_name', pattern_name)
    return HttpResponse(json.dumps('bingo'))


# 编辑页面下确认后更新数据库
def confirm_edit(request):
    try:
        pattern_name = cache.get('pattern_name')
        select_ins_type = request.POST['select_ins_type']
        info = Pattern.objects.get(pattern=pattern_name)
        # 如果编辑没有改变原来的值，则默认使用原来的值
        pattern = request.POST['pattern']
        if pattern == '':
            pattern = info.pattern
        player = request.POST['player']
        if player == '':
            player = info.player_num
        cpu = request.POST['cpu']
        if cpu == '':
            cpu = info.cpu_num
        memory = request.POST['memory']
        if memory == '':
            memory = info.memory_num
        disk = request.POST['disk']
        if disk == '':
            disk = info.disk_num
        flow = request.POST['flow']
        if flow == '':
            flow = info.flow_num
        pay_type = request.POST['pay_type']

        # 更新数据库
        Pattern.objects.filter(pattern=pattern_name).update(ins_type=select_ins_type, pattern=pattern,
                                                            player_num=player, cpu_num=cpu, memory_num=memory,
                                                            disk_num=disk, flow_num=flow, pay_type=pay_type)
        return HttpResponse('修改成功')
    except Exception as e:
        print(e)
        return HttpResponse('请检查模式名称是否已经存在')


# 模式编辑
def config_pattern_edit(request):
    pattern_name = cache.get('pattern_name')
    # 该模式的信息
    info = Pattern.objects.get(pattern=pattern_name)
    # 所有实例类型
    all_ins_type = [x[0] for x in InsType.objects.values_list('ins_type').distinct()]
    return render(request, 'config_pattern_edit.html', {'all_ins_type': all_ins_type,
                                                        'pattern_name': info.pattern,
                                                        'player_num': info.player_num,
                                                        'cpu_num': info.cpu_num,
                                                        'memory_num': info.memory_num,
                                                        'disk_num': info.disk_num,
                                                        'flow_num': info.flow_num})


# 删除模式
def pattern_delete(request):
    name = request.POST['pattern_name']
    Pattern.objects.filter(pattern=name).delete()
    return HttpResponse(json.dumps("bingo"))


# 模式添加
def config_add_pattern(request):
    # 获取现有实例所有的实例类型。在定时更新的zero_ins_type表中获取
    ins_type = [x[0] for x in InsType.objects.values_list('ins_type').distinct()]
    # 返回给前端页面以供添加模式时选择。
    return render(request, 'config_add_pattern.html', {'ins_type': ins_type})


# 模式添加存库
def config_add_pattern_confirm(request):
    try:
        instype = request.POST['ins_type']
        paytype = request.POST['pay_type']
        pattern_name = request.POST['pattern_name']
        player = request.POST['player']
        cpu = request.POST['cpu']
        memory = request.POST['memory']
        disk = request.POST['disk']
        flow = request.POST['flow']

        patt = Pattern(ins_type=instype, pay_type=paytype, pattern=pattern_name, player_num=player, cpu_num=cpu,
                       memory_num=memory, disk_num=disk, flow_num=flow)
        # 强制插入模式，防止添加模式的时候，模式名称重复
        patt.save(force_insert=True)
        return HttpResponse('bingo')
    except Exception as e:
        print(e)
        return HttpResponse('error')


# 版本编辑页面下确认后更新数据库
def version_confirm_edit(request):
    version_name = cache.get('version_name')
    info = AddVersion.objects.get(version=version_name)
    # 如果编辑没有改变原来的值，则默认使用原来的值
    version = request.POST['version']
    if version == '':
        version = info.version
    # 一个版本可以多个平台
    plat = request.POST['plat'].replace('[', '').replace(']', '').replace('"', '')
    try:
        # 编辑后更新数据库,这里会修改主键，所以只能用update方法，不能拿出主键的值在保存，因为取出之后表中就没有该数据了，只能create
        AddVersion.objects.filter(version=version_name).update(version=version, plat=plat)
        return HttpResponse('修改成功')
    except Exception as e:
        print(e)
        return HttpResponse('请检查版本名称是否已经存在')


# 版本配置
def config_version(request):
    version = AddVersion.objects.values_list('version')
    title = ['version_name']
    # 发送给前端表格的数据
    fina = []
    # 模式名称
    for v in version:
        version_server = [v[0]]
        temp = dict(zip(title, version_server))
        fina.append(temp)
    return render(request, 'config_version.html', {'data': json.dumps(fina)})


def get_version_name(request):
    version_name = request.POST['version_name']
    cache.set('version_name', version_name)
    return HttpResponse(json.dumps('bingo'))


# 版本编辑
def config_version_edit(request):
    version_name = cache.get('version_name')
    # 该版本的信息
    info = AddVersion.objects.get(version=version_name).version
    # 可以选择的平台，数据类型为列表
    plat = [x[0] for x in Plat.objects.values_list('plat')]
    return render(request, 'config_version_edit.html', {'version': info, 'plat': plat})


# 版本添加
def config_add_version(request):
    plat = [x[0] for x in Plat.objects.values_list('plat')]
    return render(request, 'config_add_version.html', {'plat': plat})


# 上传文件
def upload(request):
    file_obj = request.FILES.get('file_obj')
    filename = '/home/server/' + file_obj.name
    with open(filename, 'wb') as f:
        for chunk in file_obj.chunks():
            f.write(chunk)
    return HttpResponse('传输完成')


# 版本添加库
def config_add_version_confirm(request):
    version = request.POST['version']
    plat = request.POST['plat']
    file_obj = request.FILES.get('file_obj')
    filename = file_obj.name
    try:
        # 解压文件
        cmd = "cd /home/server; 7z x %s" % filename
        # print(cmd)
        os.system(cmd)

        # 删除压缩文件
        rmcmd = "rm -rf /home/server/%s" % filename
        os.system(rmcmd)

        # 获得解压之后的文件名
        filename = filename.replace('.7z', '')

        # 将启动服务器命令脚本拷贝至文件内
        cmd_start = "cp /home/server/start.sh /home/server/%s" % filename
        os.system(cmd_start)

        # 更改文件名，和版本名一致
        rename_cmd = "mv /home/server/%s /home/server/%s" % (filename, version)
        os.system(rename_cmd)
        # 添加版本
        add_version = AddVersion(filename=version, version=version, plat=plat)
        add_version.save(force_insert=True)
        return HttpResponse('服务器文件解压完毕，可以进行后续操作')
    except Exception as e:
        print(e)
        return HttpResponse('请检查服务器文件名是否重复')


# 删除版本
def version_delete(request):
    name = request.POST['version_name']
    AddVersion.objects.filter(version=name).delete()
    return HttpResponse(json.dumps("bingo"))


# 运营商配置
def config_run_company(request):
    run_company = [x[0] for x in RunCompany.objects.values_list('run_company_name')]
    title = ['run_company_name']
    # 发送给前端表格的数据
    fina = []
    # 模式名称
    for run in run_company:
        run_company_server = [run]
        temp = dict(zip(title, run_company_server))
        fina.append(temp)
    return render(request, 'config_run_company.html', {'data': json.dumps(fina)})


def get_run_company_name(request):
    run_company_name = request.POST['run_company_name']
    cache.set('run_company_name', run_company_name)
    return HttpResponse(json.dumps('bingo'))


# 运营商编辑
def config_run_company_edit(request):
    run_company_name = cache.get('run_company_name')
    # 该模式的信息
    info = RunCompany.objects.get(run_company_name=run_company_name).run_company_name
    return render(request, 'config_run_company_edit.html', {'run_company': info})


# 运营商编辑页面下确认后更新数据库
def run_company_confirm_edit(request):
    run_company_name = cache.get('run_company_name')
    info = RunCompany.objects.get(run_company_name=run_company_name).run_company_name
    # 如果编辑没有改变原来的值，则默认使用原来的值
    run_company = request.POST['run_company']
    if run_company == '':
        run_company = info
    try:
        RunCompany.objects.filter(run_company_name=run_company_name).update(run_company_name=run_company)
        return HttpResponse('修改成功')
    except Exception as e:
        print(e)
        return HttpResponse('请检查运营商名称是否已经存在')


# 删除运营商
def run_company_delete(request):
    name = request.POST['run_company_name']
    RunCompany.objects.filter(run_company_name=name).delete()
    return HttpResponse(json.dumps("bingo"))


# 运营商添加
def config_add_run_company(request):
    return render(request, 'config_add_run_company.html')


# 运营商添加入库
def config_add_run_company_confirm(request):
    name = request.POST['name']
    try:
        rc = RunCompany(run_company_name=name)
        rc.save(force_insert=True)
        return HttpResponse('添加成功')
    except Exception as e:
        print(e)
        return HttpResponse('运营商已经存在')


# 平台配置
def config_plat(request):
    # 查询平台，结果类型为列表
    plat = [x[0] for x in Plat.objects.values_list()]
    title = ['plat_name']
    # 发送给前端表格的数据
    fina = []
    # 模式名称
    for p in plat:
        plat_server = [p]
        temp = dict(zip(title, plat_server))
        fina.append(temp)
    return render(request, 'config_plat.html', {'data': json.dumps(fina)})


def get_plat_name(request):
    plat_name = request.POST['plat_name']
    cache.set('plat_name', plat_name)
    return HttpResponse(json.dumps('bingo'))


# 平台编辑
def config_plat_edit(request):
    plat_name = cache.get('plat_name')
    # 该模式的信息
    info = Plat.objects.get(plat=plat_name).plat
    return render(request, 'config_plat_edit.html', {'plat': info})


# 平台编辑页面下确认后更新数据库
def plat_confirm_edit(request):
    plat_name = cache.get('plat_name')
    info = Plat.objects.get(plat=plat_name).plat
    # 如果编辑没有改变原来的值，则默认使用原来的值
    plat = request.POST['plat']
    if plat == '':
        plat = info
    try:
        Plat.objects.filter(plat=plat_name).update(plat=plat)
        return HttpResponse('修改成功')
    except Exception as e:
        print(e)
        return HttpResponse('请检查平台名称是否已经存在')


# 删除运营商
def plat_delete(request):
    name = request.POST['plat_name']
    Plat.objects.filter(plat=name).delete()
    return HttpResponse(json.dumps("bingo"))


# 平台添加
def config_add_plat(request):
    return render(request, 'config_add_plat.html')


# 平台添加入库
def config_add_plat_confirm(request):
    name = request.POST['name']
    try:
        rc = Plat(plat=name)
        rc.save(force_insert=True)
        return HttpResponse('添加成功')
    except Exception as e:
        print(e)
        return HttpResponse('请检查平台名称是否已经存在')
