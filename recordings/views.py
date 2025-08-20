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

# 第三方库
from opencc import OpenCC
from transformers import pipeline
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
cc = OpenCC('t2s')  # Traditional to Simplified

def Index(request):
    context = {}
    context["hello"] = "Hello World!"
    return render(request, "index.html", context)


class sharedVariableSerializer(serializers.Serializer):
    Id = serializers.IntegerField()

    class Meta:
        fields = "__all__"

def generate_meeting_minutes(meeting_content, model="qwen3:4b",):
    """
    调用Open-WebUI API生成会议纪要
    
    参数:
        meeting_content: 会议内容文本，可以是会议记录、对话内容等
        model: 使用的模型名称，默认是qwen3:1.7b
    
    返回:
        生成的会议纪要文本，如果出错则返回None
    """
    # API端点
    url = "https://open-webui.keli.vip/api/chat/completions"
    
    # 构建提示词 - 明确要求生成结构化会议纪要
    prompt = f"""请将以下会议内容整理成一份清晰、专业的会议纪要。
会议纪要应包含以下几个部分：
1. 会议主题
2. 参会人员
3. 会议时间（如果内容中未提及可省略）
4. 会议主要内容及讨论要点
5. 决议事项
6. 行动计划（包含负责人和截止时间，如果内容中未提及可省略）

请保持语言简洁明了，重点突出，逻辑清晰。

会议内容：
{meeting_content}
"""
    
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjFiZmE1MGUyLWM1ZTEtNDcyOS05ZGE0LWZhOWE4OWUxNGY1MiJ9.J8zHA8Vsqto3CTlxZrOnOYE0mXDBHXZ_2AyminpQeA0"
    }
    
    # 请求体
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    except requests.exceptions.RequestException as e:
        print(f"API请求出错: {e}")
        return None
    except KeyError as e:
        print(f"响应解析出错: {e}")
        return None
asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small",
        chunk_length_s=30,

    generate_kwargs={"language": "zh"},  # 这是关键
)


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
        related_recordings=Recording.objects.filter(title=title)

        # 要合并的音频文件列表（按顺序）
        audio_files = []
        for recording in related_recordings:
                print("更新关联的Recording内容:", recording.audio_file)
                audio_files.append("uploads/" + str(recording.audio_file))
        merge_audios(audio_files, "uploads/" + title + ".wav")
        analysis=""



        try:
            print("Analyzing audio...","uploads/" + title + ".wav")
            result = asr("uploads/" + title + ".wav")
            transcript = result.get("text", "").strip()
            transcript=cc.convert(transcript)
            print("Analyzing audio...",transcript)
            # 生成会议纪要
            analysis = generate_meeting_minutes(transcript)
            print("ai分析成功")
        except Exception as e:
            print("ai分析失败",e)



        queryset = RecordingGroup.objects.filter(name=title)
        if queryset.exists():
            # 尝试获取已存在的对象（根据name查询）
            obj = RecordingGroup.objects.get(name=title)
            print("更新数据")
            obj.audio_file = title + ".wav" 
            obj.analysis = analysis
            obj.group.clear() 
            for recording in related_recordings:
                print("更新关联的Recording内容:", recording.audio_file)
                obj.group.add(recording) 
            obj.save()
        else:
            print("创建数据")
            # 遍历输出每个Recording的内容
            obj = RecordingGroup(name=title,audio_file=title+".wav",analysis=analysis)
            obj.save()
            
            for recording in related_recordings:
                print("Recording内容:", recording.audio_file)  # 打印整个对象
                obj.group.add(recording)

        return Response({"success": True, "transcript": ""})

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

def merge_audios(audio_files, output_file="merged_audio.wav"):
    """
    合并多个音频文件（支持不同格式/参数），输出为WAV格式
    """
    # 1. 检查输入文件
    for file in audio_files:
        if not os.path.isfile(file):
            print(f"错误：文件不存在 - {file}")
            return False
        print(f"文件存在 - {file}")
    
    # 2. 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"创建输出目录：{output_dir}")
    
    # 3. 构建ffmpeg命令（输出为WAV格式）
    input_args = []
    for file in audio_files:
        input_args.extend(["-i", file])
    
    # 音频合并滤镜（与之前一致）
    filter_args = []
    for i in range(len(audio_files)):
        filter_args.append(f"[{i}:a]")
    filter_args.append(f"concat=n={len(audio_files)}:v=0:a=1[outa]")
    filter_complex = "".join(filter_args)
    
    # 完整命令（关键修改：将编码改为pcm_s16le，去掉opus相关参数）
    cmd = [
        "ffmpeg",
        *input_args,
        "-filter_complex", filter_complex,
        "-map", "[outa]",
        "-c:a", "pcm_s16le",  # WAV标准编码（16位PCM）
        "-ar", "44100",       # 采样率（可选，默认与输入一致，指定更兼容）
        "-y",                 # 覆盖现有文件
        output_file
    ]
    print("执行命令：", " ".join(cmd))
    
    # 4. 执行命令
    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"音频合并成功！输出WAV文件：{output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"合并失败！返回码：{e.returncode}")
        print(f"ffmpeg错误输出：\n{e.stderr}")
        return False
    except Exception as e:
        print(f"发生异常：{str(e)}")
        return False

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
