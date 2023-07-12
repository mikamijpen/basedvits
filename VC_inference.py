# 原ui和cv的代码，现在已经不用了，但是可以参考一下
import os
import gradio as gr
import utils
import argparse
from models_infer import SynthesizerTrn

import numpy as np
import torch
from torch import no_grad, LongTensor
from mel_processing import spectrogram_torch
import librosa
import webbrowser
device = "cuda:0" if torch.cuda.is_available() else "cpu"

def create_vc_fn(model, hps, speaker_ids):
    def vc_fn(original_speaker, target_speaker, record_audio, upload_audio):
        input_audio = record_audio if record_audio is not None else upload_audio
        if input_audio is None:
            return "You need to record or upload an audio", None
        sampling_rate, audio = input_audio
        original_speaker_id = speaker_ids[original_speaker]
        target_speaker_id = speaker_ids[target_speaker]

        audio = (audio / np.iinfo(audio.dtype).max).astype(np.float32)
        if len(audio.shape) > 1:
            audio = librosa.to_mono(audio.transpose(1, 0))
        if sampling_rate != hps.data.sampling_rate:
            audio = librosa.resample(audio, orig_sr=sampling_rate, target_sr=hps.data.sampling_rate)
        with no_grad():
            y = torch.FloatTensor(audio)
            y = y / max(-y.min(), y.max()) / 0.99
            y = y.to(device)
            y = y.unsqueeze(0)
            spec = spectrogram_torch(y, hps.data.filter_length,
                                     hps.data.sampling_rate, hps.data.hop_length, hps.data.win_length,
                                     center=False).to(device)
            spec_lengths = LongTensor([spec.size(-1)]).to(device)
            sid_src = LongTensor([original_speaker_id]).to(device)
            sid_tgt = LongTensor([target_speaker_id]).to(device)
            audio = model.voice_conversion(spec, spec_lengths, sid_src=sid_src, sid_tgt=sid_tgt)[0][
                0, 0].data.cpu().float().numpy()
        del y, spec, spec_lengths, sid_src, sid_tgt
        return "Success", (hps.data.sampling_rate, audio)

    return vc_fn
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", default="./G_latest.pth", help="directory to your fine-tuned model")
    parser.add_argument("--config_dir", default="./finetune_speaker.json", help="directory to your model config file")
    parser.add_argument("--share", default=False, help="make link public (used in colab)")

    args = parser.parse_args()
    hps = utils.get_hparams_from_file(args.config_dir)


    net_g = SynthesizerTrn(
        len(hps.symbols),
        hps.data.filter_length // 2 + 1,
        hps.train.segment_size // hps.data.hop_length,
        n_speakers=hps.data.n_speakers,
        **hps.model).to(device)
    _ = net_g.eval()

    _ = utils.load_checkpoint(args.model_dir, net_g, None)
    speaker_ids = hps.speakers
    speakers = list(hps.speakers.keys())
    vc_fn = create_vc_fn(net_g, hps, speaker_ids)
    app = gr.Blocks()
    with app:
        gr.Markdown("""
                        录制或上传声音，并选择要转换的音色。User代表的音色是你自己。
        """)
        with gr.Column():
            record_audio = gr.Audio(label="record your voice", source="microphone")
            upload_audio = gr.Audio(label="or upload audio here", source="upload")
            source_speaker = gr.Dropdown(choices=speakers, value="User", label="source speaker")
            target_speaker = gr.Dropdown(choices=speakers, value=speakers[0], label="target speaker")
        with gr.Column():
            message_box = gr.Textbox(label="Message")
            converted_audio = gr.Audio(label='converted audio')
        btn = gr.Button("Convert!")
        btn.click(vc_fn, inputs=[source_speaker, target_speaker, record_audio, upload_audio],
                  outputs=[message_box, converted_audio])
    webbrowser.open("http://127.0.0.1:7860")
    app.launch(share=args.share)

