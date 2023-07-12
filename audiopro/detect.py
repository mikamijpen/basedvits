import librosa
from pydub import AudioSegment
import numpy as np

# MP3文件路径
filename = "1.mp3"

# 读取MP3文件
audio = AudioSegment.from_file(filename, format="mp3")

# 定义帧长度和帧间距
frame_length = 1024  # 帧长度
hop_length = 512  # 帧间距

# 定义每个片段的时长（秒）
segment_duration = 5

# 将AudioSegment对象转换为numpy数组
audio_array = np.array(audio.get_array_of_samples())

# 获取采样率
sample_rate = audio.frame_rate

# 计算片段的样本数和帧数
segment_samples = int(segment_duration * sample_rate)
segment_frames = int(segment_samples / hop_length)

# 分割音频并进行人声判断
no_vocal_segments = []
for i in range(len(audio_array) // segment_samples):
    segment = audio_array[i * segment_samples: (i + 1) * segment_samples]

    # 计算片段的RMS能量
    rms = librosa.feature.rms(y=segment, frame_length=frame_length, hop_length=hop_length)[0]
    threshold = 0.2  # 能量阈值
    has_vocal = any(rms > threshold)

    if not has_vocal:
        no_vocal_segments.append(i)

# 根据无人声片段的位置进行分割和去除操作，保存所有输出片段
output_segments = []
prev_index = 0
for index in no_vocal_segments:
    start_time = prev_index * segment_duration * 1000  # 转换为毫秒
    end_time = index * segment_duration * 1000

    output_segments.append(audio[start_time:end_time])

    prev_index = index + 1

# 添加最后一个片段
output_segments.append(audio[prev_index * segment_duration * 1000:])

# 合并所有输出片段
output_audio = sum(output_segments)

# 保存去除无人声部分的音频文件
output_path = "output.mp3"
output_audio.export(output_path, format="mp3")

print("保存完成，输出文件：", output_path)
