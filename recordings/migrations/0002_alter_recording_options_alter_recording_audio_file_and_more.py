# Generated by Django 5.2.4 on 2025-07-31 14:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recordings", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="recording",
            options={"verbose_name": "录音", "verbose_name_plural": "录音"},
        ),
        migrations.AlterField(
            model_name="recording",
            name="audio_file",
            field=models.FileField(
                upload_to="recordings/%Y/%m/%d/", verbose_name="音频文件"
            ),
        ),
        migrations.AlterField(
            model_name="recording",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="上传时间"),
        ),
        migrations.AlterField(
            model_name="recording",
            name="duration",
            field=models.FloatField(
                blank=True, help_text="单位：秒", null=True, verbose_name="音频时长"
            ),
        ),
        migrations.AlterField(
            model_name="recording",
            name="title",
            field=models.CharField(blank=True, max_length=255, verbose_name="录音标题"),
        ),
        migrations.AlterField(
            model_name="recording",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recordings",
                to=settings.AUTH_USER_MODEL,
                verbose_name="上传用户",
            ),
        ),
    ]
