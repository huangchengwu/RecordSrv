from .serializers import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http.response import HttpResponse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import render
from opencc import OpenCC
from django_filters.rest_framework import DjangoFilterBackend

cc = OpenCC('t2s')  # Traditional to Simplified
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from transformers import pipeline
import torchaudio
import os
from vosk import Model, KaldiRecognizer
import wave
import json

def Index(request):
    context = {}
    context["hello"] = "Hello World!"
    return render(request, "index.html", context)


class sharedVariableSerializer(serializers.Serializer):
    Id = serializers.IntegerField()

    class Meta:
        fields = "__all__"


class sharedVariable(GenericAPIView):
    serializer_class = sharedVariableSerializer

    def get(self, request, *args, **krgs):

        return Response("1", status=status.HTTP_201_CREATED)


# # ✅ 模型只加载一次（全局作用域）
asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small",
        chunk_length_s=30,

    generate_kwargs={"language": "zh"},  # 这是关键
)

# 只加载一次模型（建议设置绝对或相对路径）
# vosk_model_path = os.path.join("static", "vosk-model-small-cn-0.22")
# vosk_model = Model(vosk_model_path)


# class RecordingViewSet(ModelViewSet):
#     queryset = Recording.objects.all()
#     serializer_class = RecordingSerializer
#     permission_classes = [IsAuthenticated]


#     @action(detail=True, methods=["post"], url_path="analyze")

#     def analyze(self, request, pk=None):
#         """
#         使用 Vosk 中文模型分析音频，生成文本摘要，保存在 analysis 字段
#         """
#         recording = self.get_object()
#         audio_path = recording.audio_file.path

#         if not os.path.exists(audio_path):
#             return Response({"error": "音频文件不存在"}, status=404)

#         # 确保音频是 16kHz 单声道 wav 格式
#         try:
#             wf = wave.open(audio_path, "rb")
#             if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
#                 return Response({"error": "请转换音频为 16kHz 单声道 16位 PCM 格式的 .wav 文件"}, status=400)

#             rec = KaldiRecognizer(vosk_model, wf.getframerate())
#             result_text = ""

#             while True:
#                 data = wf.readframes(4000)
#                 if len(data) == 0:
#                     break
#                 if rec.AcceptWaveform(data):
#                     res = json.loads(rec.Result())
#                     result_text += res.get("text", "") + " "

#             res = json.loads(rec.FinalResult())
#             result_text += res.get("text", "")

#             wf.close()

#             recording.analysis = result_text
#             recording.save()

#             return Response({"success": True, "transcript": result_text})
#         except Exception as e:
#             return Response({"error": str(e)}, status=500)



class RecordingViewSet(ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id','user', 'title', 'created_at']

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

    # # 过滤
    # filter_fields = ("id", "htmlName")
    # # 排序
    # ordering_fields = "id"

    # # 自定义方法
    # @action(methods=["post"], detail=False, url_path="exec_task")
    # def exec_task(self, request, *args, **kwargs):
    #     print(request.method, args, kwargs, request.data)
    #     dd = {"w": "ww", "ee": "ttt"}

    #     return Response(dd)
