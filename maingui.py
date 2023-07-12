import os
import shutil
import tkinter as tk  # 使用Tkinter前需要先导入
from tkinter import messagebox

import time

import winsound
from langdetect import detect  # 导入语言检测库

from main import *

text = ''
sendMsg = ''
fname = ''


def send(myphoto):
    global sendMsg, text, fname
    t1_Msg.configure(state=tk.NORMAL)
    sendMsg = t2_sendMsg.get('0.0', 'end')
    if sendMsg == '':
        tk.messagebox.showinfo(title='attention!', message='please input japanese！')
    else:
        lang = detect(sendMsg)  # 检测文本的语言

        if lang != "ja" and lang != "en":  # 如果不是日语，英语
            tk.messagebox.showinfo(title='attention!', message='please input japanese！')
            t2_sendMsg.delete("1.0", "end")  # 清空t2_sendMsg的内容

        else:
            strMsg = '（既読）' + time.strftime("%Y-%m-%d %H:%M", time.localtime()) + ":mikami" + '\n'
            text += strMsg + '|'
            t1_Msg.insert("end", strMsg, 'Gright')  # 我靠右
            t1_Msg.image_create('end', image=myphoto, padx=335, pady=5)  # 插入图片
            t1_Msg.insert("end", '\n', 'Gright')

            t1_Msg.insert("end", sendMsg, 'right')
            text += sendMsg + '|'
            t2_sendMsg.delete('1.0', "end")
            app.update()  # 强制刷新界面
            name, response, fname = out(sendMsg)
            response = response.replace('\n', '')

            # 直接输出到t1_Msg
            strMsg = name + ":" + time.strftime("%Y-%m-%d %H:%M", time.localtime()) + '（既読）'
            text += strMsg + '|'

            t1_Msg.insert("end", '\n' + strMsg + '\n', 'Rleft')  # 对方靠左
            if name[0] == 'T':
                t1_Msg.image_create('end', image=herphoto, pady=5)  # 插入图片
            else:
                t1_Msg.image_create('end', image=herphoto2, pady=5)
            t1_Msg.insert("end", '\n', 'Rleft')
            t1_Msg.insert("end", response + '\n', 'left')
            text += response + '|'

    t1_Msg.configure(state=tk.DISABLED)


def replay(path):
    winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)  # 播放音频


def rgb_to_hex(r, g, b):
    # 将rbg数值转化为16进制字符串
    r_hex = hex(r)[2:].zfill(2)  # 去掉0x前缀，补齐两位
    g_hex = hex(g)[2:].zfill(2)
    b_hex = hex(b)[2:].zfill(2)
    # 拼接成16进制颜色码
    hex_code = "#" + r_hex + g_hex + b_hex
    return str(hex_code)


app = tk.Tk()
app.title('Line')
photo = tk.PhotoImage(file=r'C:\Users\Administrator\Desktop\chat\line.png')  # 创建图片对象
app.wm_iconphoto(False, photo)  # 指定图片对象
#
w = 421
h = 625
width = 37
sw = app.winfo_screenwidth()
sh = app.winfo_screenheight()
x = (sw - w) / 4
y = (sh - h) / 2
app.geometry("%dx%d+%d+%d" % (w, h, x, y))
app.resizable(width=False, height=False)  # 禁止调整窗口大小

l = tk.Label(app, text='家族組（3）', bg=rgb_to_hex(49, 60, 82), fg='white', font=('Arial', 15, 'bold'), width=60,
             height=2)
l.pack()
# 重放
menu_button = tk.Menubutton(app, text=' 再 生 ', bg=rgb_to_hex(49, 60, 82), fg='white', font=('Arial', 12))
menu_button.place(x=365, y=25)
menu = tk.Menu(menu_button, tearoff=False)
menu_button.config(menu=menu)  # 用菜单按钮绑定菜单

# 重放音频文件
folder_path = r'C:\Users\Administrator\Desktop\chat'
files = os.listdir(folder_path)
audio_files = [file for file in files if file.endswith('.mp3') or file.endswith('.wav')]
if audio_files:
    for file in audio_files:
        menu.add_command(label=file, command=lambda f=file: replay(os.path.join(folder_path, f)))  # 添加菜单项

else:
    menu.add_command(label='No audio files found', command=lambda: None)

# 聊天消息预览窗口


t1_Msg = tk.Text(width=width, height=22, font=('Arial', 14), wrap=tk.CHAR, bg=rgb_to_hex(224, 227, 236),
                 highlightbackground=rgb_to_hex(49, 60, 82), highlightthickness=5, undo=True)

t1_Msg.tag_config('right', justify=tk.RIGHT, background=rgb_to_hex(142, 205, 97), foreground='white',
                  offset=10)
t1_Msg.tag_config('Gright', justify=tk.RIGHT, foreground='green', font=('Arial', 10))
t1_Msg.tag_config('left', justify=tk.LEFT, foreground='white', background=rgb_to_hex(244, 116, 164),
                  offset=10)
t1_Msg.tag_config('Rleft', justify=tk.LEFT, foreground='red', font=('Arial', 10))

t1_Msg.place(x=0, y=53)
scroll = tk.Scrollbar()

# 两个控件关联
scroll.config(command=t1_Msg.yview)
t1_Msg.config(yscrollcommand=scroll.set)

# 聊天消息发送窗口
t2_sendMsg = tk.Text(width=32, height=3, font=('Arial', 14), wrap=tk.WORD,
                     highlightbackground=rgb_to_hex(245, 245, 245),
                     highlightthickness=5)
scroll2 = tk.Scrollbar()

# 两个控件关联
scroll2.config(command=t2_sendMsg.yview)
t2_sendMsg.config(yscrollcommand=scroll2.set)
t2_sendMsg.place(x=0, y=545)

from PIL import Image, ImageTk

image = Image.open(r"C:\Users\Administrator\Desktop\chat\m.jpg")  # 打开jpg文件
myphoto = ImageTk.PhotoImage(image)  # 准备加头像
image2 = Image.open(r"C:\Users\Administrator\Desktop\chat\h.jpg")  # 打开jpg文件
herphoto = ImageTk.PhotoImage(image2)  # 准备加头像
image3 = Image.open(r"C:\Users\Administrator\Desktop\chat\t2.jpg")  # 打开jpg文件
herphoto2 = ImageTk.PhotoImage(image3)  # 准备加头像


def save():
    global fname
    source_folder = r'C:\Users\Administrator\Desktop\chat\temp'
    target_folder = r'C:\Users\Administrator\Desktop\chat'

    file_path = os.path.join(source_folder, fname)
    if file_path.endswith(".wav"):
        shutil.move(file_path, target_folder)
    else:
        print("文件格式不符合要求")
    menu.add_command(label=file, command=lambda f=fname: replay(os.path.join(target_folder, f)))  # 直接更新菜单项

    with open("text_data.txt", "a") as f:  # 追加写入
        f.write(text)


# 从文件中加载保存的数据


with open("text_data.txt", "r") as f:
    data = f.read()
    data = data.split('|')
    data = data[:-1]  # 去掉最后一个空元素

    if len(data) % 4 == 0:
        # 四四取出元素
        iter_obj = iter(data)
        for t1, t2, t3, t4 in zip(*[iter(data)] * 4):
            t1_Msg.insert("end", t1, 'Gright')  # 我靠右
            t1_Msg.image_create('end', image=myphoto, padx=335, pady=5)  # 插入图片
            t1_Msg.insert("end", '\n', 'Gright')
            t1_Msg.insert("end", t2, 'right')

            t1_Msg.insert("end", '\n' + t3 + '\n', 'Rleft')  # 对方靠左
            if t3[0] == 'T':
                t1_Msg.image_create('end', image=herphoto, pady=5)  # 插入图片
            else:
                t1_Msg.image_create('end', image=herphoto2, pady=5)
            t1_Msg.insert("end", '\n', 'Rleft')
            t1_Msg.insert("end", t4 + '\n', 'left')
    else:
        print('wrong data')
t1_Msg.see("end")

send_button = tk.Button(app, text='  発 送  ', bg=rgb_to_hex(90, 131, 231), fg='white', font=('Arial', 10),
                        command=lambda: [send(myphoto)])
send_button.place(x=365, y=545)

save_button = tk.Button(app, text="  保 存  ", bg=rgb_to_hex(90, 131, 231), fg='white', font=('Arial', 10),
                        command=save)
save_button.place(x=365, y=598)

# def scroll_up():
#     t1_Msg.yview_scroll(-10, 'units')
start = tk.END  # 从文本的最后一行开始搜索
def jump_to_last_occurrence():
    global start
    keyword ='mikami' # 获取输入的关键词

    index = t1_Msg.search(keyword, start, backwards=True, stopindex="1.0")  # 倒序搜索包含关键词的行

    if index:
        # 定位到找到的行
        t1_Msg.mark_set(tk.INSERT, index)
        t1_Msg.see(index)
        t1_Msg.focus_set()
        start = index + "-1c"  # 从找到的行的前一行开始搜索
    else:
        print("关键词未找到！")

button = tk.Button(app, text='めくる ',bg=rgb_to_hex(90, 131, 231), fg='white', font=('Arial', 10), command=jump_to_last_occurrence,pady=-1)
button.place(x=365, y=572)

# 退出时删除临时文件夹
def before_close():
    folder_path = r'C:\Users\Administrator\Desktop\chat\temp'
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            # 如果是文件夹，就递归删除
            os.rmdir(file_path)
    app.destroy()


app.protocol("WM_DELETE_WINDOW", before_close)
app.mainloop()
