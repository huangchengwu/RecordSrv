from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from RecordSrv.tasks import *

# 第三方库
from opencc import OpenCC

import torchaudio
from vosk import Model, KaldiRecognizer
import wave
import json
import subprocess
import os
import tempfile
import requests

# 本地导入
from .serializers import *

# 初始化简繁转换工具


def Index(request):
    context = {}
    context["hello"] = "Hello World!"
    return render(request, "index.html", context)

class sharedVariableSerializer(serializers.Serializer):
    Id = serializers.IntegerField()

    class Meta:
        fields = "__all__"
class analyze_Serializer(serializers.Serializer):
    title = serializers.CharField()
    # audio_files = serializers.ListField(
    #     child=serializers.CharField(),  # 列表中的元素是字符串（文件路径）
    #     required=False  # 可选字段，可根据需求设为必填（默认必填）
    # )
    class Meta:
        fields = "__all__"
class analyze_recording(GenericAPIView):
    serializer_class = analyze_Serializer
    def post(self, request, *args, **krgs):
        title = request.data.get("title")
        # audio_files = request.data.get("audio_files")

        generate_meeting_minutes_task.delay("qwen3:1.7b",title)

        return Response({"success": True, "transcript": "等待执行成功"})
class RecordingGroupViewSet(ModelViewSet):
    queryset = RecordingGroup.objects.all()
    serializer_class = RecordingGroupSerializer
    permission_classes = [IsAuthenticated]
    ##支持过滤
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['Id','name', 'group', 'analysis','created_at','updated_at']
    #合并音频分析

class RecordingViewSet(ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer
    permission_classes = [IsAuthenticated]
    ##支持过滤
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'title', 'created_at']
    #合并音频分析
     
    #ai分析

    @action(detail=True, methods=["post"], url_path="analyze")
    def analyze(self, request, pk=None):
        """
        使用 Whisper 模型分析音频，生成文本摘要，保存在 analysis 字段
        """
        recording = self.get_object()
        audio_path = recording.audio_file.path
        if not os.path.exists(audio_path):
            return Response({"error": "音频文件不存在"}, status=404)
        try:
            # waveform, sample_rate = torchaudio.load(audio_path)
            # result = asr({"array": waveform[0].numpy(), "sampling_rate": sample_rate})
            # recording.analysis = result["text"]
            # recording.save()
            print("Analyzing audio...",audio_path)
            result = asr(audio_path)
            transcript = result.get("text", "").strip()

            transcript=cc.convert(transcript)

            print("Analyzing audio...",transcript)


            recording.analysis = transcript
            recording.save()
            
            return Response({"success": True, "transcript": transcript})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

