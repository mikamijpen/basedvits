from pydub import AudioSegment
import math

# MP3文件路径
filename = 'output.mp3'

# 每个片段的时长（毫秒）
segment_duration = 10 * 60 * 1000

# 读取音频文件
audio = AudioSegment.from_mp3(filename)

# 计算片段数量
num_segments = math.ceil(len(audio) / segment_duration)

# 分割音频并保存每个片段
for i in range(num_segments):
    start_time = i * segment_duration
    end_time = (i + 1) * segment_duration

    segment = audio[start_time:end_time]

    # 创建输出文件名
    output_filename = f"segment_{i + 1}.mp3"

    # 保存片段
    segment.export(output_filename, format="mp3")

    print("保存片段：", output_filename)
