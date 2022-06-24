# @Time : 2022/6/5 16:40 
# @Author : kongsh
# @File : server.py
from django.shortcuts import HttpResponse, render, redirect
from django.http import JsonResponse
from web import models
from web.forms.server import ServerModelForm


def server_list(request):
    """
    查看所有的服务器信息
    :param request:
    :return:
    """
    queryset = models.Server.objects.all()
    return render(request, "server_list.html", {'queryset': queryset})


def server_add(request):
    """
    添加服务器
    :param request:
    :return:
    """
    if request.method == "GET":
        form = ServerModelForm()
        return render(request, 'form.html', {'form': form})
    else:
        # 接收用户数据进行表单验证
        form = ServerModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('server_list')
        else:
            return render(request, 'form.html', {'form': form})


def server_edit(request, sid):
    """
    编辑服务器信息
    :param request:
    :return:
    """
    obj = models.Server.objects.filter(id=sid).first()

    if request.method == "GET":
        form = ServerModelForm(instance=obj)
        return render(request, 'form.html', {'form': form})
    else:
        # 接收用户数据进行表单验证
        form = ServerModelForm(data=request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('server_list')
        else:
            return render(request, 'form.html', {'form': form})


def server_del(request, sid):
    """
    删除指定的服务器
    :param request:
    :param sid:
    :return:
    """
    models.Server.objects.filter(id=sid).delete()
    return JsonResponse({'status': 'success'})
