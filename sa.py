from gtts import gTTS

# 开会讲解稿（你可以改成自己的内容）
meeting_text = """
各位同事，大家上午好。
今天的会议主要有三个议题：
第一，回顾上季度的工作进展和存在的问题；
第二，讨论下季度的重点目标和任务分配；
第三，确定新的项目推进计划。
请大家在讨论过程中积极发言，提出建设性的意见。
谢谢大家的参与。
"""

# 生成语音文件
tts = gTTS(meeting_text, lang="zh-cn")
tts.save("meeting_guide.mp3")

print("会议讲解音频已保存为 meeting_guide.mp3")
