import os
import gradio as gr
import utils
import argparse
import commons
from models import SynthesizerTrn
from text import text_to_sequence
import torch
from torch import no_grad, LongTensor
import soundfile as sf

audio_postprocess_ori = gr.Audio.postprocess
limitation = os.getenv("SYSTEM") == "spaces"  # limit text and audio length

parser = argparse.ArgumentParser()
parser.add_argument('--device', type=str, default='cpu')
args = parser.parse_args()

device = torch.device(args.device)

# 也许可以分离做函数
hps_ms = utils.get_hparams_from_file(r'C:\Users\Administrator\Desktop\chat\30.json')
net_g_ms = SynthesizerTrn(
    len(hps_ms.symbols),
    hps_ms.data.filter_length // 2 + 1,
    hps_ms.train.segment_size // hps_ms.data.hop_length,
    n_speakers=hps_ms.data.n_speakers,
    **hps_ms.model)
_ = net_g_ms.eval().to(device)
speakers = hps_ms.speakers
model, optimizer, learning_rate, epochs = utils.load_checkpoint(r'C:\Users\Administrator\Desktop\chat\30.pth',
                                                                net_g_ms, None)


def get_text(text, hps):
    text_norm, clean_text = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm, clean_text


def vits(text, language, speaker_id, noise_scale, noise_scale_w, length_scale):
    if not len(text):
        return "输入文本不能为空！", None, None
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

text='そして、なぜ3日でできるものを1か月も作っていないと思っているのかと疑問に思います。'

# import playsound
import winsound
import time
from characterai import errors

sr, audio = vits(text, 1, torch.tensor([0]), 0.5, 0.2, 1.5)  # 0表示中文，1表示日文，只有一个说话人用tensor0
# 适合帝皇的是0.7,1,1
# noise_scale: 这是一个控制语音合成中噪声水平的参数，它影响了语音的清晰度和自然度。
# 一般来说，噪声水平越低，语音越清晰，但也越生硬；噪声水平越高，语音越模糊，但也越柔和。
# noise_scale_w: 这是一个控制语音合成中噪声频率的参数，它影响了语音的音高和音色。
# 一般来说，噪声频率越低，语音越低沉，但也越沉闷；噪声频率越高，语音越尖锐，但也越刺耳。
# length_scale: 这是一个控制语音合成中语速的参数，它影响了语音的节奏和韵律。
# 一般来说，越小语速越快，语音越紧凑，但也越难懂

now = time.localtime()  # 获取当前的时间
fname = time.strftime("%Y_%m_%d_%H_%M_%S", now) + '.wav'  # 格式化时间为字符串，作为文件名
purpose_dir = r'C:\Users\Administrator\Desktop'

sf.write(os.path.join(purpose_dir, fname), audio, samplerate=sr)  # 保存音频
path = os.path.join(purpose_dir, fname)
winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)  # 异步播放音频
