import os
import gradio as gr
import utils
import argparse
import commons
from models_infer import SynthesizerTrn
from text import text_to_sequence
import torch
from torch import no_grad, LongTensor
import soundfile as sf

who=1 # 1:帝皇 2:姐姐

audio_postprocess_ori = gr.Audio.postprocess
limitation = os.getenv("SYSTEM") == "spaces"  # limit text and audio length

parser = argparse.ArgumentParser()
parser.add_argument('--device', type=str, default='cpu')
args = parser.parse_args()

device = torch.device(args.device)
if who == 1:
    hps_ms = utils.get_hparams_from_file(r'C:\Users\Administrator\Desktop\chat\帝皇.json')
else:
    hps_ms = utils.get_hparams_from_file(r'C:\Users\Administrator\Desktop\chat\40.json')
net_g_ms = SynthesizerTrn(
    len(hps_ms.symbols),
    hps_ms.data.filter_length // 2 + 1,
    hps_ms.train.segment_size // hps_ms.data.hop_length,
    n_speakers=hps_ms.data.n_speakers,
    **hps_ms.model)
_ = net_g_ms.eval().to(device)
speakers = hps_ms.speakers
if who == 1:
    model, optimizer, learning_rate, epochs = utils.load_checkpoint(r'C:\Users\Administrator\Desktop\chat\帝皇.pth',
                                                                net_g_ms, None)
else:
    model, optimizer, learning_rate, epochs = utils.load_checkpoint(r'C:\Users\Administrator\Desktop\chat\40.pth',
                                                                net_g_ms, None)

def get_text(text, hps):
    text_norm, clean_text = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm, clean_text


def vits(text, language, speaker_id, noise_scale, noise_scale_w, length_scale):
    if not len(text):
        return "输入文本不能为空", None, None
    text = text.replace('\n', ' ').replace('\r', '').replace(" ", "")
    if len(text) > 500 and limitation:
        return f"输入文字过长！{len(text)}>500", None, None
    if language == 0:
        text = f"[ZH]{text}[ZH]"
    elif language == 1:
        text = f"[JA]{text}[JA]"
    else:
        text = f"{text}"
    stn_tst, clean_text = get_text(text, hps_ms)
    with no_grad():
        x_tst = stn_tst.unsqueeze(0).to(device)
        x_tst_lengths = LongTensor([stn_tst.size(0)]).to(device)
        speaker_id = LongTensor([speaker_id]).to(device)
        # tensor([132]) 0.1 0.668 1.1
        audio = \
            net_g_ms.infer(x_tst, x_tst_lengths, sid=speaker_id, noise_scale=noise_scale, noise_scale_w=noise_scale_w,
                           length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()

    return 22050, audio


from characterai import PyCAI
client = PyCAI('')# token记得删
if who == 1:
    char = 'piwvxvcMQFwbQXCQpJdzbqPMg9ck4FaYi4NWM86ERXo'# 帝皇
else:
    char = 'thep9Jza4nSUQQ_ok7YCEI2uMim5oH9OXcVUyo5-C7E'  # 助手

# Save tgt and history_external_id to avoid making a lot of requests
chat = client.chat.get_chat(char)

history_id = chat['external_id']
participants = chat['participants']

# In the list of "participants",
# a character can be at zero or in the first place
if not participants[0]['is_human']:
    tgt = participants[0]['user']['username']
else:
    tgt = participants[1]['user']['username']

# import playsound
import winsound
import time
from characterai import errors


def out(message):
    while True:  # 循环，直到成功发送
        try:
            data = client.chat.send_message(
                char, message, history_external_id=history_id, tgt=tgt, filtering=False, wait=True
            )
            name = data['src_char']['participant']['name']
            text = data['replies'][0]['text']
            text = text.replace('Training ', '訓練')
            text = text.replace('-', '')

            if who == 1:
                sr, audio = vits(text, 1, torch.tensor([0]), 0.5, 0.9, 1)  # 0表示中文�?1表示日文，只有一个说话人用tensor0
            else:
                sr, audio = vits(text, 1, torch.tensor([0]), 0.2, 0.2, 1.1)  # 0表示中文�?1表示日文，只有一个说话人用tensor0

            # 适合帝皇的是0.7,1,1
            # noise_scale: 这是一个控制语音合成中噪声水平的参数，它影响了语音的清晰度和自然度�?
            # 一般来说，噪声水平越低，语音越清晰，但也越生硬；噪声水平越高，语音越模糊，但也越柔和�?
            # noise_scale_w: 这是一个控制语音合成中噪声频率的参数，它影响了语音的音高和音色�?
            # 一般来说，噪声频率越低，语音越低沉，但也越沉闷；噪声频率越高，语音越尖锐，但也越刺耳�?
            # length_scale: 这是一个控制语音合成中语速的参数，它影响了语音的节奏和韵律�?
            # 一般来说，越小语速越快，语音越紧凑，但也越难�?

            now = time.localtime()  # 获取当前的时�?
            fname = time.strftime("%Y_%m_%d_%H_%M_%S", now) + '.wav'  # 格式化时间为字符串，作为文件�?
            purpose_dir = r'C:\Users\Administrator\Desktop\chat\temp'

            sf.write(os.path.join(purpose_dir, fname), audio, samplerate=sr)  # 保存音频
            print(f"{name}:{text}")
            path = os.path.join(purpose_dir, fname)
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)  # 异步播放音频
            if name[0] != 'T':
                name = '天音姉'
            return name, text, fname

        except errors.Loaded:  # 如果发送失败，等待15s后重�?
            print('waiting')
            time.sleep(15)
