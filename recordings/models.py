from django.db import models
from django.contrib.auth.models import User


class Recording(models.Model):
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
        verbose_name="音频文件"
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
