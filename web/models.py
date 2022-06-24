from django.db import models


class Server(models.Model):
    """
    服务器表
    """
    hostname = models.CharField(verbose_name="主机名", max_length=32)

    def __str__(self):
        return self.hostname


class Project(models.Model):
    """项目表"""
    title = models.CharField(verbose_name="项目名", max_length=32)
    repo = models.CharField(verbose_name="仓库地址", max_length=128)
    evn_choice = (
        ("prod", "正式环境"),
        ("test", "测试环境"),
    )
    env = models.CharField(verbose_name="环境", max_length=16, choices=evn_choice, default="test")
    path = models.CharField(verbose_name="线上项目地址", max_length=128)
    servers = models.ManyToManyField(verbose_name="关联服务器", to="Server")

    def __str__(self):
        return "%s - %s" % (self.title, self.get_env_display())


class Deploy(models.Model):
    """发布任务表"""
    project = models.ForeignKey(verbose_name="项目环境", to="Project", on_delete=models.CASCADE)
    tag = models.CharField(verbose_name="发布版本", max_length=32)
    # 项目-test-v1-20220610121212
    uid = models.CharField(verbose_name="标识", max_length=64)
    status_choices = (
        (1, "待发布"),
        (2, "发布中"),
        (3, "成功"),
        (4, "失败"),
    )
    status = models.IntegerField(verbose_name="状态", choices=status_choices, default=1)

    # 可扩展的钩子
    before_download_script = models.TextField(verbose_name="下载前脚本", null=True, blank=True)
    after_download_script = models.TextField(verbose_name="下载后脚本", null=True, blank=True)
    before_deploy_script = models.TextField(verbose_name="发布前脚本", null=True, blank=True)
    after_deploy_script = models.TextField(verbose_name="发布后脚本", null=True, blank=True)

    def __str__(self):
        return "[%s]- [%s]" % (self.project.title, self.tag)


class HookTemplate(models.Model):
    """钩子模板"""
    title = models.CharField(verbose_name="模板名称", max_length=64)
    content = models.TextField(verbose_name="脚本内容")
    hook_type_choices = (
        (2, '下载前'),
        (4, '下载后'),
        (6, '发布前'),
        (8, '发布后'),
    )
    hook_type = models.IntegerField(verbose_name="钩子类型", choices=hook_type_choices)

    def __str__(self):
        return self.title


class Node(models.Model):
    """节点表"""
    task = models.ForeignKey(verbose_name="发布任务单", to='Deploy', on_delete=models.CASCADE)
    text = models.CharField(verbose_name="节点文字", max_length=32)
    status_choices = (
        ("lightgrey", "待发布"),
        ("green", "成功"),
        ("red", "失败"),
    )
    status = models.CharField(verbose_name="状态", max_length=16, choices=status_choices, default='lightgrey')
    parent = models.ForeignKey(verbose_name="父节点", to="self", null=True, blank=True, on_delete=models.CASCADE)
    server = models.ForeignKey(verbose_name="服务器", to="Server", null=True, blank=True, on_delete=models.CASCADE)












