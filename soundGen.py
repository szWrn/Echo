# -*- coding: utf-8 -*-
"""
根据左右声道的 时间差（ITD）与 响度（ILD），生成五个方向的立体声 WAV：
前、左、右、左前、右前，保存到 audio 文件夹。
"""
from __future__ import annotations

import os
import wave

import numpy as np

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(ROOT_DIR, "audio")

# 五方向：左(0)、左前(1)、前(2)、右前(3)、右(4)
# 每项：(左声道延迟ms, 右声道延迟ms, 左声道增益, 右声道增益)
# 声源在左 → 左耳先到 → 右声道延迟；声源在右 → 左声道延迟。增益表示响度比。
DIRECTION_PARAMS = (
    (0.0, 0.5, 1.0, 0.0),   # 0 左：右声道延迟 0.5ms，仅左响
    (0.0, 0.25, 1.0, 0.5),  # 1 左前：右延迟 0.25ms，左强右弱
    (0.0, 0.0, 1.0, 1.0),   # 2 前：无时差，双声道等响
    (0.25, 0.0, 0.5, 1.0),  # 3 右前：左延迟 0.25ms，左弱右强
    (0.5, 0.0, 0.0, 1.0),   # 4 右：左声道延迟 0.5ms，仅右响
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


def apply_delay(signal: np.ndarray, delay_ms: float, sample_rate: int) -> np.ndarray:
    """
    对单声道信号施加延迟（毫秒）。延迟通过前补零、后截断实现。
    返回与 signal 等长的 float32 数组。
    """
    if delay_ms <= 0:
        return signal.astype(np.float32)
    delay_samples = int(round(delay_ms * sample_rate / 1000.0))
    if delay_samples <= 0:
        return signal.astype(np.float32)
    n = len(signal)
    out = np.zeros(n, dtype=np.float32)
    copy_len = n - delay_samples
    if copy_len > 0:
        out[delay_samples:] = signal[:copy_len]
    return out


def generate_direction_audio(
    delay_left_ms: float,
    delay_right_ms: float,
    gain_l: float,
    gain_r: float,
    tone: np.ndarray,
    sample_rate: int,
) -> np.ndarray:
    """
    根据左右声道 时间差 与 响度 生成立体声交错数据（float32）。
    返回 shape=(len(tone)*2,) 的数组，交错为 L,R,L,R,...
    """
    left_raw = apply_delay(tone, delay_left_ms, sample_rate)
    right_raw = apply_delay(tone, delay_right_ms, sample_rate)
    left = (left_raw * gain_l).astype(np.float32)
    right = (right_raw * gain_r).astype(np.float32)
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
    根据左右声道 时间差 与 响度（及基准 volume_l/volume_r），生成五个方向的 WAV 并保存到 audio 目录。
    use_direction_index_names=True 时保存为 k0.wav~k4.wav，供 direction.py 直接使用。
    返回保存的文件路径列表。
    """
    os.makedirs(AUDIO_DIR, exist_ok=True)
    tone = generate_tone(duration_sec=duration_sec, sample_rate=sample_rate, frequency=frequency)
    saved = []

    for i, (name_cn, name_en) in enumerate(zip(DIRECTION_NAMES, OUTPUT_NAMES)):
        delay_l_ms, delay_r_ms, gain_l, gain_r = DIRECTION_PARAMS[i]
        gl = gain_l * volume_l
        gr = gain_r * volume_r
        stereo = generate_direction_audio(
            delay_left_ms=delay_l_ms,
            delay_right_ms=delay_r_ms,
            gain_l=gl,
            gain_r=gr,
            tone=tone,
            sample_rate=sample_rate,
        )
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
