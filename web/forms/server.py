# @Time : 2022/6/5 17:39 
# @Author : kongsh
# @File : server.py
from django.forms import ModelForm
from django import forms
from web import models
import datetime


class BaseModelForm(ModelForm):
    """modelfrom基类"""
    exclude_bootstrap_field = []

    def __init__(self, *args, **kwargs):
        # 执行父类的构造方法
        super().__init__(*args, **kwargs)
        # 自定义功能
        for name, field in self.fields.items():
            if name in self.exclude_bootstrap_field:
                continue
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入' + field.label


class ServerModelForm(BaseModelForm):
    """server 表的modelform"""
    class Meta:
        model = models.Server
        fields = "__all__"


class ProjectModelForm(BaseModelForm):
    """project 表的modelform"""
    class Meta:
        model = models.Project
        fields = "__all__"


class TaskModelForm(BaseModelForm):
    """Task 表的modelform"""
    exclude_bootstrap_field = ['before_download_template', 'after_download_template',
                               'before_deploy_template', 'after_deploy_template']
    # 自定义的字段
    before_download_select = forms.ChoiceField(required=False, label="下载前")
    before_download_title = forms.CharField(required=False, label="模板名称")
    before_download_template = forms.CharField(required=False, widget=forms.CheckboxInput, label="是否保存为模板")

    after_download_select = forms.ChoiceField(required=False, label="下载后")
    after_download_title = forms.CharField(required=False, label="模板名称")
    after_download_template = forms.CharField(required=False, widget=forms.CheckboxInput, label="是否保存为模板")

    before_deploy_select = forms.ChoiceField(required=False, label="发布前")
    before_deploy_title = forms.CharField(required=False, label="模板名称")
    before_deploy_template = forms.CharField(required=False, widget=forms.CheckboxInput, label="是否保存为模板")

    after_deploy_select = forms.ChoiceField(required=False, label="发布后")
    after_deploy_title = forms.CharField(required=False, label="模板名称")
    after_deploy_template = forms.CharField(required=False, widget=forms.CheckboxInput, label="是否保存为模板")

    class Meta:
        model = models.Deploy
        # fields = "__all__"
        exclude = ['uid', 'project', 'status']

    def __init__(self, project, *args, **kwargs):
        """初始化方法"""
        super(TaskModelForm, self).__init__(*args, **kwargs)
        self.project = project
        self._init_hook()

    def _init_hook(self):
        """初始化钩子模板"""
        before_download = [(0, "请选择")]
        before_download.extend(models.HookTemplate.objects.filter(hook_type=2).values_list('id', 'title'))
        self.fields['before_download_select'].choices = before_download

        after_download = [(0, "请选择")]
        after_download.extend(models.HookTemplate.objects.filter(hook_type=4).values_list('id', 'title'))
        self.fields['after_download_select'].choices = after_download

        before_deploy = [(0, "请选择")]
        before_deploy.extend(models.HookTemplate.objects.filter(hook_type=6).values_list('id', 'title'))
        self.fields['before_deploy_select'].choices = before_deploy

        after_deploy = [(0, "请选择")]
        after_deploy.extend(models.HookTemplate.objects.filter(hook_type=8).values_list('id', 'title'))
        self.fields['after_deploy_select'].choices = after_deploy

    def save(self, commit=True):
        # 增加隐藏的字段
        self.instance.project_id = self.project.id
        self.instance.uid = self._create_uid()
        super().save(commit)

        # 保存模板钩子
        if eval(self.cleaned_data.get('before_download_template')):
            title = self.cleaned_data.get('before_download_title')
            content = self.cleaned_data.get('before_download_script')
            models.HookTemplate.objects.create(title=title,
                                               content=content,
                                               hook_type=2)

        if eval(self.cleaned_data.get('after_download_template')):
            title = self.cleaned_data.get('after_download_title')
            content = self.cleaned_data.get('after_download_script')
            models.HookTemplate.objects.create(title=title,
                                               content=content,
                                               hook_type=4)

        if eval(self.cleaned_data.get('before_deploy_template')):
            title = self.cleaned_data.get('before_deploy_title')
            content = self.cleaned_data.get('before_deploy_script')
            models.HookTemplate.objects.create(title=title,
                                               content=content,
                                               hook_type=6)

        if eval(self.cleaned_data.get('after_deploy_template')):
            title = self.cleaned_data.get('after_deploy_title')
            content = self.cleaned_data.get('after_deploy_script')
            models.HookTemplate.objects.create(title=title,
                                               content=content,
                                               hook_type=8)

    def _create_uid(self):
        """生成uid"""
        title = self.project.title
        env = self.project.env
        tag = self.cleaned_data.get('tag')
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return "{0}-{1}-{2}-{3}".format(title, env, tag, now)

    def clean(self):
        """表单校验的最后一个环节"""
        if eval(self.cleaned_data.get('before_download_template')):
            title = self.cleaned_data.get('before_download_title')
            if not title:
                self.add_error("before_download_title", "请输入模板名称")

        if eval(self.cleaned_data.get('after_download_template')):
            title = self.cleaned_data.get('after_download_title')
            if not title:
                self.add_error("after_download_title", "请输入模板名称")

        if eval(self.cleaned_data.get('before_deploy_template')):
            title = self.cleaned_data.get('before_deploy_title')
            if not title:
                self.add_error("before_deploy_title", "请输入模板名称")

        if eval(self.cleaned_data.get('after_deploy_template')):
            title = self.cleaned_data.get('after_deploy_title')
            if not title:
                self.add_error("after_deploy_title", "请输入模板名称")

