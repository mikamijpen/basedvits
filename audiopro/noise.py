from pydub import AudioSegment
import noisereduce as nr

# 读取MP3文件
audio = AudioSegment.from_file("output.mp3", format="mp3")

# 将AudioSegment对象转换为numpy数组
audio_array = audio.get_array_of_samples()

# 获取采样率
sample_rate = audio.frame_rate

# 执行降噪
reduced_audio_array = nr.reduce_noise(audio_array, sr=sample_rate)

# 将降噪后的数组转换回AudioSegment对象
reduced_audio = AudioSegment(
    reduced_audio_array.tobytes(),
    frame_rate=audio.frame_rate,
    sample_width=audio.sample_width,
    channels=audio.channels
)

reduced_audio.export("output2.mp3", format="mp3")
