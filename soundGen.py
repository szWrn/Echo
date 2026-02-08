# -*- coding: utf-8 -*-
"""
根据左右声道音量比例，生成五个方向的立体声 WAV：
前、左、右、左前、右前，保存到 audio 文件夹。
"""
from __future__ import annotations

import os
import wave
import struct

import numpy as np

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(ROOT_DIR, "audio")

# 五方向：左(0)、左前(1)、前(2)、右前(3)、右(4)
# 每个方向 (左声道增益, 右声道增益)，范围 0~1
DIRECTION_GAINS = (
    (1.0, 0.0),   # 0 左：仅左声道
    (1.0, 0.5),   # 1 左前：左强右弱
    (1.0, 1.0),   # 2 前：双声道等响
    (0.5, 1.0),   # 3 右前：左弱右强
    (0.0, 1.0),   # 4 右：仅右声道
)

DIRECTION_NAMES = ("左", "左前", "前", "右前", "右")
OUTPUT_NAMES = ("left", "front_left", "front", "front_right", "right")


def generate_tone(
    duration_sec: float = 0.5,
    sample_rate: int = 22050,
    frequency: float = 440.0,
) -> np.ndarray:
    """生成单声道正弦波（float32，-1~1）。"""
    n = int(duration_sec * sample_rate)
    t = np.arange(n, dtype=np.float64) / sample_rate
    tone = np.sin(2 * np.pi * frequency * t).astype(np.float32)
    return tone


def generate_direction_audio(
    gain_l: float,
    gain_r: float,
    tone: np.ndarray,
) -> np.ndarray:
    """
    根据左右声道增益生成立体声交错数据（float32）。
    返回 shape=(len(tone)*2,) 的数组，交错为 L,R,L,R,...
    """
    left = (tone * gain_l).astype(np.float32)
    right = (tone * gain_r).astype(np.float32)
    stereo = np.empty(len(tone) * 2, dtype=np.float32)
    stereo[0::2] = left
    stereo[1::2] = right
    return stereo


def float32_stereo_to_int16(stereo_float: np.ndarray) -> bytes:
    """将交错 float32 立体声裁剪到 [-1,1] 并转为 16 位 PCM 字节。"""
    stereo_float = np.clip(stereo_float, -1.0, 1.0)
    stereo_int16 = (stereo_float * 32767).astype(np.int16)
    return stereo_int16.tobytes()


def generate_and_save_all(
    duration_sec: float = 0.5,
    sample_rate: int = 22050,
    frequency: float = 440.0,
    volume_l: float = 1.0,
    volume_r: float = 1.0,
    output_prefix: str = "dir",
    use_direction_index_names: bool = False,
) -> list[str]:
    """
    根据左右声道基准音量 volume_l、volume_r，生成五个方向的 WAV 并保存到 audio 目录。
    use_direction_index_names=True 时保存为 k0.wav~k4.wav，供 direction.py 直接使用。
    返回保存的文件路径列表。
    """
    os.makedirs(AUDIO_DIR, exist_ok=True)
    tone = generate_tone(duration_sec=duration_sec, sample_rate=sample_rate, frequency=frequency)
    saved = []

    for i, (name_cn, name_en) in enumerate(zip(DIRECTION_NAMES, OUTPUT_NAMES)):
        gain_l, gain_r = DIRECTION_GAINS[i]
        gl = gain_l * volume_l
        gr = gain_r * volume_r
        stereo = generate_direction_audio(gl, gr, tone)
        pcm_bytes = float32_stereo_to_int16(stereo)

        if use_direction_index_names:
            filename = f"k{i}.wav"
        else:
            filename = f"{output_prefix}_{name_en}.wav"
        filepath = os.path.join(AUDIO_DIR, filename)
        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_bytes)
        saved.append(filepath)
        print(f"已生成：{name_cn} -> {filepath}")

    return saved


if __name__ == "__main__":
    # 左右声道基准音量 1.0；use_direction_index_names=True 则生成 k0~k4.wav 供 direction.py 使用
    generate_and_save_all(volume_l=1.0, volume_r=1.0, use_direction_index_names=True)
