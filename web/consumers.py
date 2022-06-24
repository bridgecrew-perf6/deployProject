# @Time : 2022/6/4 9:22 
# @Author : kongsh
# @File : consumers.py
import json
import time
import threading
import os
import subprocess
import shutil
import traceback
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
from django.conf import settings
from web import models
from utils.git_util import GitRepository
from utils.ssh import SSHProxy


consumer_object_list = []


def get_node(task_obj, task_id):
    """返回节点数据"""
    node_obj_list = []
    queryset = models.Node.objects.filter(task_id=task_id)
    if queryset:
        return queryset

    # 没有的话在数据库创建节点
    start_node = models.Node.objects.create(text="开始", task_id=task_id)
    node_obj_list.append(start_node)
    # 判断第1个钩子是否有自定义脚本：任务单对象.before_download_script
    if task_obj.before_download_script:
        start_node = models.Node.objects.create(text='下载前', task_id=task_id, parent=start_node)
        node_obj_list.append(start_node)

    download_node = models.Node.objects.create(text="下载", task_id=task_id, parent=start_node)
    node_obj_list.append(download_node)

    # 判断第2个钩子是否有自定义脚本：任务单对象.after_download_script
    if task_obj.after_download_script:
        download_node = models.Node.objects.create(text='下载后', task_id=task_id, parent=download_node)
        node_obj_list.append(download_node)

    upload_node = models.Node.objects.create(text="上传", task_id=task_id, parent=download_node)
    node_obj_list.append(upload_node)

    task_obj = models.Deploy.objects.filter(id=task_id).first()
    for server_obj in task_obj.project.servers.all():
        row = models.Node.objects.create(text=server_obj.hostname,
                                         task_id=task_id,
                                         parent=upload_node,
                                         server=server_obj)
        node_obj_list.append(row)
        # 判断是否有发布前钩子
        if task_obj.before_deploy_script:
            row = models.Node.objects.create(text="发布前",
                                             task_id=task_id,
                                             parent=row,
                                             server=server_obj)
            node_obj_list.append(row)

        deploy_node = models.Node.objects.create(text="发布",
                                                 task_id=task_id,
                                                 parent=row,
                                                 server=server_obj)
        node_obj_list.append(deploy_node)

        # 判断是否有发布后钩子
        if task_obj.after_deploy_script:
            row = models.Node.objects.create(text="发布后",
                                             task_id=task_id,
                                             parent=deploy_node,
                                             server=server_obj)
            node_obj_list.append(row)

    return node_obj_list


def convert_obj_to_gojs(node_obj_list):
    """将对象列表转换为gojs识别的json格式"""
    node_list = []
    for node in node_obj_list:
        tmp = {
            'key': str(node.id),
            'text': node.text,
            'color': node.status,
            'stroke': 'white',
        }
        if node.parent:
            tmp['parent'] = str(node.parent.id)
        node_list.append(tmp)
    return node_list


class PublishConsumer(WebsocketConsumer):

    def websocket_connect(self, message):
        """
        请求websocket链接时自动触发
        :param message:
        :return:
        """
        # 与客户端建立链接
        self.accept()
        # 将自己加入到task_id群里，接收以后发来的消息
        # 【固定写法】获取url中传递的参数,如果url中定义的是关键字参数，就用kwargs,否则就用args
        task_id = self.scope['url_route']['kwargs'].get('task_id')
        async_to_sync(self.channel_layer.group_add)(task_id, self.channel_name)

        # 用户打开页面时，如果已经创建好节点则直接返回
        queryset = models.Node.objects.filter(task_id=task_id)
        if queryset:
            node_list = convert_obj_to_gojs(queryset)
            self.send(text_data=json.dumps({'code': 'init', 'data': node_list}))

    def websocket_receive(self, message):
        """
        客户端发送消息时自动触发
        :param message:
        :return:
        """
        # print("客户端消息：", message)
        task_id = self.scope['url_route']['kwargs'].get('task_id')
        task_obj = models.Deploy.objects.filter(id=task_id).first()

        text = message.get('text')
        if text == 'init':
            # node_list = [
            #     {'key': "start", 'text': '开始', 'figure': 'Ellipse'},
            #     {'key': "download", 'parent': 'start', 'text': '下载代码', 'link_text': '执行中...'},
            #     {'key': "compile", 'parent': 'download', 'text': '本地编译'},
            # ]

            # 第1步:数据库没有的话先创建节点，有的话直接读取
            node_obj_list = get_node(task_obj, task_id)

            # 第2步:根据对象列表封装好指定格式数据，以json格式返回给gojs
            node_list = convert_obj_to_gojs(node_obj_list)

            # self.send(text_data=json.dumps({'code': 'init', 'data': node_list}))
            # 第1个参数是群号；
            # 第2个参数是给这个群内的每个用户发送消息的函数；
            # 第3个参数是发送的消息
            async_to_sync(self.channel_layer.group_send)(task_id,
                                                         {'type': 'xxx.yyy',
                                                          'message': {'code': 'init', 'data': node_list}})

        if text == 'deploy':
            # 代码发布
            # channels的缺陷，有sleep的时候，颜色在最后统一展示，不能逐个展示，需要将执行函数放到另外一个线程
            task = threading.Thread(target=self.deploy, args=(task_id, task_obj))
            task.start()

    def xxx_yyy(self, event):
        """发送消息函数，会给每个用户都发送message字段中的内容"""
        message = event['message']
        self.send(json.dumps(message))

    def websocket_disconnect(self, message):
        """断开websocket链接时触发"""
        task_id = self.scope['url_route']['kwargs'].get('task_id')
        # 群聊里剔除离开的用户,self.channel_name相当于给每个人创建的唯一id
        async_to_sync(self.channel_layer.group_discard)(task_id, self.channel_name)

        raise StopConsumer()

    def _change_node_status(self, text, task_id, server=None, color='green'):
        """
        修改指定节点的状态和颜色
        :param text:
        :param server:主机
        :param task_id:
        :param color:修改后的颜色
        :return:
        """
        if server:
            node = models.Node.objects.filter(text=text, task_id=task_id, server=server).first()
        else:
            node = models.Node.objects.filter(text=text, task_id=task_id).first()
        node.status = color
        node.save()
        # 群发
        async_to_sync(self.channel_layer.group_send)(task_id,
                                                     {'type': 'xxx.yyy',
                                                      'message': {'code': 'update', 'node_id': node.id,
                                                                  'color': node.status}})

    def _send_log(self, task_id, info):
        """实时输出日志信息"""
        # 群发
        async_to_sync(self.channel_layer.group_send)(task_id,
                                                     {'type': 'xxx.yyy',
                                                      'message': {'code': 'log', 'info': info}})

    def _create_script_and_run(self, script_folder, script_name, task_obj, run=True):
        """创建指定脚本并执行"""
        script_path = os.path.join(script_folder, script_name)
        status = 'green'
        script = script_name.split('.')[0]
        try:
            with open(script_path, 'w', encoding='utf-8') as fp:
                fp.write(task_obj.__getattribute__(script))
            # 判断是否需要执行脚本：
            if run is True:
                # shell=True：命令可以有空格
                cmd = "python {0}".format(script_name)
                subprocess.check_output(cmd, shell=True, cwd=script_folder)
                self._send_log(str(task_obj.id), '>>>' + str(cmd))
        except Exception as e:
            print(e)
            self._send_log(str(task_obj.id), '<<<' + str(e))
            status = 'red'
        else:
            self._send_log(str(task_obj.id), '<<< success')
        return status

    def deploy(self, task_id, task_obj):
        """代码发布"""
        project_name = task_obj.project.title
        uid = task_obj.uid
        script_folder = os.path.join(settings.DEPLOY_CODE_PATH, project_name, uid, "script")
        project_folder = os.path.join(settings.DEPLOY_CODE_PATH, project_name, uid, project_name)
        package_folder = os.path.join(settings.PACKAGE_PATH, project_name)
        if not os.path.exists(script_folder):
            os.makedirs(script_folder)
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
        if not os.path.exists(package_folder):
            os.makedirs(package_folder)

        # step1:找到数据库中的开始节点，改变颜色，同时将状态给前端返回
        self._change_node_status('开始', task_id)

        # step2: 下载前
        if task_obj.before_download_script:
            # TODO:执行一些具体的动作，比如执行钩子脚本
            # 在发布机三执行钩子脚本的内容
            # 1.将钩子脚本的内容写入到本地脚本文件；
            # 2.在本地执行这个脚本，如果成功则status为green，否则为red
            status = self._create_script_and_run(script_folder, 'before_download_script.py', task_obj)
            self._change_node_status('下载前', task_id, color=status)
            # 脚本执行失败，直接退出
            if status == "red":
                return

        # step3: 下载
        # 1.获取仓库地址：task_obj.project.repo
        # 2.去git仓库拉取代码：git clone -b
        self._send_log(task_id, '>>> git clone -b %s %s' % (task_obj.project.repo, task_obj.tag))
        status = 'green'
        try:
            GitRepository(project_folder, task_obj.project.repo, task_obj.tag)
        except Exception as e:
            status = 'red'
            self._send_log(task_id, '<<<' + str(e))

        self._change_node_status('下载', task_id, color=status)
        if status == 'red':
            return

        # step4: 下载后
        if task_obj.after_download_script:
            status = self._create_script_and_run(script_folder, 'after_download_script.py', task_obj)
            self._change_node_status('下载后', task_id, color=status)
            # 脚本执行失败，直接退出
            if status == "red":
                return

        # step5：上传
        self._change_node_status('上传', task_id)
        time.sleep(2)

        # step6：链接每台服务器
        # 提前生成before_deploy_script和after_deploy_script脚本，一起上传
        if task_obj.before_deploy_script:
           self._create_script_and_run(script_folder, 'before_deploy_script.py', task_obj, run=False)
        if task_obj.after_deploy_script:
           self._create_script_and_run(script_folder, 'after_deploy_script.py', task_obj, run=False)

        remote_folder = os.path.join(settings.SERVER_PACKAGE_PATH, project_name) + '/'
        remote_pro_folder = remote_folder + uid + '/'

        for server_obj in task_obj.project.servers.all():
            # step 6.1: 上传代码
            # TODO，通过paramiko将代码上传到服务器
            # 1.python代码将文件打包
            upload_folder_path = os.path.join(settings.DEPLOY_CODE_PATH, project_name, uid)
            zip_file = uid + '.zip'
            remote_zip_folder = remote_folder + zip_file
            try:
                package_path = shutil.make_archive(
                    base_name=os.path.join(package_folder, zip_file),# 压缩后的存储路径
                    format='zip',# 压缩格式：zip、tar
                    root_dir=upload_folder_path,# 被压缩的文件夹路径
                )
                # 2.将压缩文件上传到服务器
                with SSHProxy(server_obj.hostname, settings.SSH_PORT, settings.SSH_USER, settings.SSH_PWD) as ssh:
                    remote_folder = os.path.join(settings.SERVER_PACKAGE_PATH, project_name)
                    cmd = 'mkdir -p {0}'.format(remote_folder)
                    res, err = ssh.command(cmd)
                    self._send_log(str(task_obj.id), '>>>' + cmd)
                    if err:
                        self._send_log(str(task_obj.id), '>>>' + err.encode('utf-8'))
                    ssh.upload(package_path, remote_folder + "/" + zip_file)
            except Exception as e:
                print("step6：链接每台服务器:", traceback.print_exc())
                self._send_log(str(task_obj.id), '<<<' + str(e))
                status = 'red'
            self._change_node_status(server_obj.hostname, task_id, server_obj, color=status)
            if status == 'red':
                continue

            # step 6.2: 发布前的钩子
            if task_obj.before_deploy_script:
                # ###############方案一
                # 1.在本地生成脚本文件
                # 2.将脚本上传到服务器
                # 3.脚本上传到服务器并执行

                # ###############方案二【推荐】
                # 1.代码上传之前，将脚本写入到code/项目/uid/script目录下
                # 2.上传代码后，将代码解压
                with SSHProxy(server_obj.hostname, settings.SSH_PORT, settings.SSH_USER, settings.SSH_PWD) as ssh:
                    result, err = ssh.command('unzip  -d {0} {1}'.format(remote_pro_folder, remote_zip_folder))
                    print(err)
                    # 3.执行脚本
                    result, err = ssh.command("python {0}".format(remote_pro_folder + 'script/before_deploy_script.py'))
                    print(err)
                    if err:
                        status = 'red'
                self._change_node_status("发布前", task_id, server_obj, color=status)
                if status == 'red':
                    continue

            # step 6.3: 发布
            self._change_node_status("发布", task_id, server_obj)

            # step 6.4: 发布后的钩子
            if task_obj.after_deploy_script:
                self._change_node_status("发布后", task_id, server_obj)

