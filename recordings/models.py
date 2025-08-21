from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import time 
class Recording(models.Model):
    Id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='recordings',
        verbose_name="上传用户"
    )
    title = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="录音标题"
    )
    audio_file = models.FileField(
        upload_to='recordings/%Y/%m/%d/',  # 自动按日期分类文件夹
        verbose_name="音频文件",
                default=''

    )
    duration = models.FloatField(
        help_text="单位：秒", 
        null=True, 
        blank=True, 
        verbose_name="音频时长"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="上传时间"
    )
    analysis = models.TextField(verbose_name="ai分析", default="")

    class Meta:
        verbose_name = "录音"
        verbose_name_plural = "录音"

    def __str__(self):
        return self.title or f"Recording #{self.pk}"







class RecordingGroup(models.Model):
    # 定义状态选项：元组格式 (存储值, 显示名称)
    STATUS_CHOICES = [
        ('unanalyzed', '未分析'),  # 初始状态，未进行AI分析
        ('analyzing', '分析中'),   # 正在执行AI分析任务
        ('completed', '分析完成'), # AI分析成功完成
        ('failed', '分析失败'),    # AI分析出错
    ]
    
    Id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=255, verbose_name="录音组", default="", unique=True
    )
    audio_file = models.FileField(
        upload_to='recordinggroup/%Y/%m/%d/',  # 自动按日期分类文件夹
        verbose_name="音频文件",
        null=True,  # 允许数据库中存储 NULL 值
        blank=True,  # 允许表单提交时为空（管理员界面或表单验证时生效）
        default=''  # 保持默认空字符串（可选，根据需求决定是否保留）
    )
    group = models.ManyToManyField(Recording)
    # 新增状态字段
    status = models.CharField(
        max_length=20,
        verbose_name="状态",
        choices=STATUS_CHOICES,
        default='unanalyzed',  # 默认初始状态为“未分析”
    )

    analysis = models.TextField(verbose_name="ai分析", default="")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "录音组"
        verbose_name_plural = verbose_name

