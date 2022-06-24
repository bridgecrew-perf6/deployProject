# @Time : 2022/6/5 16:40 
# @Author : kongsh
# @File : project.py
from django.shortcuts import HttpResponse, render, redirect
from django.http import JsonResponse
from web import models
from web.forms.server import ProjectModelForm


def project_list(request):
    """
    查看所有的项目信息
    :param request:
    :return:
    """
    queryset = models.Project.objects.all()
    return render(request, "project_list.html", {'queryset': queryset})


def project_add(request):
    """
    添加项目
    :param request:
    :return:
    """
    if request.method == "GET":
        form = ProjectModelForm()
        return render(request, 'form.html', {'form': form})
    else:
        # 接收用户数据进行表单验证
        form = ProjectModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
        else:
            return render(request, 'form.html', {'form': form})


def project_edit(request, sid):
    """
    编辑项目信息
    :param request:
    :return:
    """
    obj = models.Project.objects.filter(id=sid).first()

    if request.method == "GET":
        form = ProjectModelForm(instance=obj)
        return render(request, 'form.html', {'form': form})
    else:
        # 接收用户数据进行表单验证
        form = ProjectModelForm(data=request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('project_list')
        else:
            return render(request, 'form.html', {'form': form})


def project_del(request, sid):
    """
    删除指定的项目
    :param request:
    :param sid:
    :return:
    """
    models.Project.objects.filter(id=sid).delete()
    return JsonResponse({'status': 'success'})
