from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import queue
q_dict = {}


def home(request):
    """聊天页"""
    user = request.GET.get('name')
    # 为每个用户定义一个队列
    q_dict[user] = queue.Queue()
    return render(request, 'home.html', locals())


def send_msg(request):
    """客户端发送消息"""
    # if request.method == "POST":
    # 获取用户提交内容，并将其放入所有的用户队列
    msg = request.GET.get('msg')
    for q in q_dict.values():
        q.put(msg)
    return JsonResponse({"status": True})


def get_msg(request):
    """客户端获取消息"""
    name = request.GET.get('name')
    q = q_dict.get(name)
    result = {"status": True, 'msg': ''}
    try:
        data = q.get(timeout=10)
        result['msg'] = data
    except queue.Empty as e:
        result['status'] = False

    return JsonResponse(result)


def index(request):
    """基于channels的聊天室"""
    # 为每个用户定义一个队列
    return render(request, 'index.html', locals())


def demo(request):
    """演示用"""
    return render(request, 'gojsDemo.html')
