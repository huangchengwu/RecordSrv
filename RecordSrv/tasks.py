from celery import shared_task
from django.conf import settings  # noqa
import requests
import json
import subprocess
import os
from transformers import pipeline
from opencc import OpenCC
from recordings.models import *
from django.conf import settings



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
        "-filter_complex",
        filter_complex,
        "-map",
        "[outa]",
        "-c:a",
        "pcm_s16le",  # WAV标准编码（16位PCM）
        "-ar",
        "44100",  # 采样率（可选，默认与输入一致，指定更兼容）
        "-y",  # 覆盖现有文件
        output_file,
    ]
    print("执行命令：", " ".join(cmd))

    # 4. 执行命令
    try:
        result = subprocess.run(
            cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
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


# 封装执行
@shared_task(soft_time_limit=300, track_started=True)
def generate_meeting_minutes_task(
     model, title
):
    related_recordings=Recording.objects.filter(title=title)

    asr = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-small",
        chunk_length_s=30,
        generate_kwargs={"language": "zh"},  # 这是关键
    )
    cc = OpenCC("t2s")  # Traditional to Simplified
    # 要合并的音频文件列表（按顺序）
    print( model, title, related_recordings)
     
    audio_files = []
    for recording in related_recordings:
        print("更新关联的Recording内容:", recording.audio_file)
        audio_files.append("uploads/" + str(recording.audio_file))
    merge_audios(audio_files, "uploads/" + title + ".wav")
    analysis = ""
    try:
        print("Analyzing audio...", "uploads/" + title + ".wav")
        result = asr("uploads/" + title + ".wav")
        transcript = result.get("text", "").strip()
        transcript = cc.convert(transcript)
        print("Analyzing audio...", transcript)
        # 生成会议纪要
        # analysis = generate_meeting_minutes(transcript)
        print("ai分析成功")
    except Exception as e:
        print("ai分析失败", e)
    print("请求数据")
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
        {transcript}
        """

    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.OPENWEBUI_API_KEY}",

    }

    # 请求体
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    print("配置内容",url,prompt,data,headers)
    analysis = ""
    try:
        # 发送请求
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # 检查请求是否成功

        # 解析响应
        result = response.json()
        analysis = result["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        print(f"API请求出错: {e}")

    except KeyError as e:
        print(f"响应解析出错: {e}")

    queryset = RecordingGroup.objects.filter(name=title)
    if queryset.exists():
        # 尝试获取已存在的对象（根据name查询）
        obj = RecordingGroup.objects.get(name=title)
        print("分析结果",analysis)
        obj.audio_file = title + ".wav"
        obj.analysis = analysis
        
        obj.group.clear()
        
        obj.status = 'analyzing'  # 成功则更新为完成

        for recording in related_recordings:
            print("更新关联的Recording内容:", recording.audio_file)
            obj.group.add(recording)
        obj.status = 'completed'  # 成功则更新为完成

        obj.save()
    else:
        print("创建数据")
        # 遍历输出每个Recording的内容
        obj = RecordingGroup(name=title, audio_file=title + ".wav", analysis=analysis)
        obj.status = 'analyzing'  # 成功则更新为完成
        print("分析结果",analysis)
        obj.save()

        for recording in related_recordings:
            print("Recording内容:", recording.audio_file)  # 打印整个对象
            obj.group.add(recording)
        obj.status = 'completed'  # 成功则更新为完成

        obj.save()
