# Generated by Django 3.1.6 on 2022-06-12 09:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_hooktemplate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=32, verbose_name='节点文字')),
                ('status', models.CharField(choices=[('grey', '待发布'), ('green', '成功'), ('red', '失败')], max_length=16, verbose_name='状态')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.node', verbose_name='父节点')),
                ('server', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.server', verbose_name='服务器')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.deploy', verbose_name='发布任务单')),
            ],
        ),
    ]
