# @Time : 2022/6/5 16:40 
# @Author : kongsh
# @File : deploy.py
from django.shortcuts import HttpResponse, render, redirect
from django.urls import reverse
from django.http import JsonResponse
from web import models
from web.forms.server import TaskModelForm


def task_list(request, pid):
    """发布任务列表"""
    project_obj = models.Project.objects.filter(id=pid).first()
    task_list = models.Deploy.objects.filter(project_id=pid)
    return render(request, 'task_list.html', {'queryset': task_list, 'project_obj': project_obj})


def task_add(request, pid):
    """创建发布任务单"""
    project_obj = models.Project.objects.filter(id=pid).first()
    if request.method == "GET":
        form = TaskModelForm(project=project_obj)
        return render(request, 'task_form.html', {'form': form, 'project_obj': project_obj})
    form = TaskModelForm(project=project_obj, data=request.POST)
    if form.is_valid():
        form.save()
        url = reverse('task_list', kwargs={'pid': pid})
        return redirect(url)
    return render(request, 'task_form.html', {'form': form, 'project_obj': project_obj})


def hook_template(request, tid):
    """返回指定模板内容"""
    hook_template_obj = models.HookTemplate.objects.filter(id=tid).first()
    return JsonResponse({"status": True, 'content': hook_template_obj.content})


def deploy(request, task_id):
    """发布任务"""
    task_obj = models.Deploy.objects.filter(id=task_id).first()
    return render(request, "deploy.html", {'task_obj': task_obj})