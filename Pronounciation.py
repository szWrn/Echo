from models.TTS import *
from Server import *
from threading import Thread
import time
import json
import random

HOST = "0.0.0.0"
PORT = 5001
server = Server(HOST, PORT)
server_thread = Thread(target=server.run)
server_thread.start()

with open("practice/chars.json", "r", encoding="utf-8") as f:
    chars = json.load(f)
question = None
answer = None
index = ["A", "B", "C", "D"]


def sendToClients(text):
    for client in server.clients:
        client.sendall(bytes(text + "\n", "utf-8"))


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


if __name__ == '__main__':
    init_dashscope_api_key()
    tts = TTSProcess(TTSCallback())
    tts.setup()
    while True:
        question = random.choice(chars)
        answer = random.randint(0, 3)
        choices = question["chars"]
        answer_str = choices[answer]
        question_str = ""
        for i in range(4):
            question_str += f"{index[i]}.{choices[i]}"
        print(question_str)
        sendToClients(question_str)
        tts.send_text("请选出以下汉字:" + answer_str)
        user_answer = listen_one_sentence()
        if index[answer] in user_answer:
            sendToClients("回答正确")
            tts.send_text("回答正确")
        else:
            sendToClients("回答错误")
            tts.send_text("回答错误")

