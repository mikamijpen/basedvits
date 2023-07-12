import os
import librosa

# 文件夹路径
folder_path = r"C:\Users\Administrator\Desktop\long_audios"

# 获取文件夹中的MP3文件列表
mp3_files = [file for file in os.listdir(folder_path) if file.endswith(".mp3")]

# 计算每个MP3文件的RMS能量
file_rms = []
for mp3_file in mp3_files:
    file_path = os.path.join(folder_path, mp3_file)
    audio, sr = librosa.load(file_path, sr=None)
    rms = librosa.feature.rms(y=audio)[0].mean()
    file_rms.append((mp3_file, rms))

# 按照RMS能量从高到低排序
sorted_files = sorted(file_rms, key=lambda x: x[1])

# 输出排序结果
for file, rms in sorted_files:
    print(f"文件名: {file}，RMS能量: {rms}")
delete_count = len(sorted_files) // 3 * 2 # 删除数量为2/3
for i in range(delete_count):
    file_to_delete = sorted_files[i][0]
    file_path = os.path.join(folder_path, file_to_delete)
    os.remove(file_path)
    print(f"已删除文件: {file_to_delete}")