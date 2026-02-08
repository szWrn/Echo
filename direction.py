# -*- coding: utf-8 -*-
"""
声音定位：播放某方向声音 -> 用户口述方向 -> ASR 转文字 -> 程序判对错，循环进行。
方向：左(0)、左前(1)、前(2)、右前(3)、右(4)
"""
from __future__ import annotations

import os
import sys
from typing import Optional
import time
import wave

import pyaudio

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(ROOT_DIR, "audio")

# 五个方向：0=左, 1=左前, 2=前, 3=右前, 4=右
DIRECTION_NAMES = ("左", "左前", "前", "右前", "右")

# 用户说法 -> 方向索引（多种说法映射到 0-4）
DIRECTION_MAP = {
    "左前": 1,
    "左前方": 1,
    "1": 1,
    "一": 1,
    "右前": 3,
    "右前方": 3,
    "3": 3,
    "三": 3,
    "左": 0,
    "左边": 0,
    "0": 0,
    "零": 0,
    "前": 2,
    "前面": 2,
    "正前": 2,
    "前方": 2,
    "2": 2,
    "二": 2, 
    "两": 2,
    "右": 4,
    "右边": 4,
    "4": 4,
    "四": 4,
}


def play_wav(file_path: str) -> None:
    """用 PyAudio 播放单个 WAV 文件。"""
    with wave.open(file_path, "rb") as wf:
        rate = wf.getframerate()
        channels = wf.getnchannels()
        width = wf.getsampwidth()
        p = pyaudio.PyAudio()
        fmt = pyaudio.paInt16 if width == 2 else p.get_format_from_width(width)
        stream = p.open(format=fmt, channels=channels, rate=rate, output=True)
        chunk = 1024
        data = wf.readframes(chunk)
        while data:
            stream.write(data)
            data = wf.readframes(chunk)
        stream.stop_stream()
        stream.close()
        p.terminate()


def listen_one_sentence():
    """
    打开 ASR，录到用户说完一句后返回识别文本。
    每次调用会新建 Recognition，录完一句后 stop 并关闭流。
    """
    import models.ASR as asr_module
    from dashscope.audio.asr import Recognition

    asr_module.init_dashscope_api_key()
    result_holder = {"text": "", "done": False}

    def on_sentence_end(text):
        result_holder["text"] = (text or "").strip()
        result_holder["done"] = True

    callback = asr_module.ASRCallback(on_sentence_end=on_sentence_end, chat=None)
    recognition = Recognition(
        model="paraformer-realtime-v2",
        format=asr_module.format_pcm,
        sample_rate=asr_module.sample_rate,
        semantic_punctuation_enabled=False,
        callback=callback,
    )
    recognition.start()

    # 等待麦克风在 on_open 里打开
    for _ in range(100):
        if getattr(asr_module, "streamInput", None) is not None:
            break
        time.sleep(0.05)
    stream_input = getattr(asr_module, "streamInput", None)
    if stream_input is None:
        recognition.stop()
        return ""

    block_size = getattr(asr_module, "block_size", 3200)
    try:
        while not result_holder["done"]:
            data = stream_input.read(block_size, exception_on_overflow=False)
            recognition.send_audio_frame(data)
    except Exception:
        pass
    recognition.stop()
    return result_holder.get("text", "")


def text_to_direction_index(text: str) -> Optional[int]:
    """把用户说的内容归一化为方向索引 0-4，无法识别返回 None。"""
    if not text:
        return None
    text = text.strip().replace(" ", "")
    for key, value in DIRECTION_MAP.items():
        if key in text:
            return value
    return None


def main():
    import random

    print("声音定位：程序播放某方向声音，您听后说出方向（左/左前/前/右前/右），程序判断对错。")
    print("方向对应：左=0, 左前=1, 前=2, 右前=3, 右=4")
    print("按 Ctrl+C 退出。\n")

    # 使用 k0.wav ~ k4.wav 对应方向 0~4；若不存在则尝试 v0~v4
    def get_audio_path(index: int) -> str:
        for prefix in ("k", "v"):
            p = os.path.join(AUDIO_DIR, f"{prefix}{index}.wav")
            if os.path.isfile(p):
                return p
        raise FileNotFoundError(f"未找到方向 {index} 的音频，请准备 audio/k{index}.wav 或 v{index}.wav")

    while True:
        correct = random.randint(0, 4)
        path = get_audio_path(correct)
        print(f"请听声辨位 → 正在播放：{DIRECTION_NAMES[correct]}（{path}）")
        play_wav(path)
        print("请说出您认为的声源方向（左 / 左前 / 前 / 右前 / 右）…")
        user_text = listen_one_sentence()
        print(f"识别结果：{user_text!r}")
        user_index = text_to_direction_index(user_text)
        print(f"user_index: {user_index}")
        if user_index is None:
            print("未能识别您的回答，请重试。\n")
            continue
        if correct == user_index:
            print("回答正确。\n")
        else:
            print(f"回答错误，正确答案是：{DIRECTION_NAMES[correct]}（{correct}）。\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已退出。")
        sys.exit(0)
