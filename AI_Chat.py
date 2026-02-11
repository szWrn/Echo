import dashscope
from models import TTS, ASR
from models.api import init_dashscope_api_key
from dashscope.audio.asr import *
import Server
from threading import Thread
import time
import json

with open('reports/index.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    index = int(lines[0].strip())
    f.close()
with open("reports/index.txt", "w", encoding="utf-8") as f:
    f.write(str(index + 1))
question_index = 0

HOST = "0.0.0.0"
PORT = 5001
server = Server.Server(HOST, PORT)
server_thread = Thread(target=server.run, daemon=True)
server_thread.start()

messages = [
    {'role':'system','content':'你是一个帮助人工耳蜗术后患者恢复听力的AI,目的是训练接受过人工耳蜗植入手术的用户更好地理解和使用中文。你要说几句话，让用户重复，可以加入一些近音字，判断他们对话沟通中出现的问题(如某处对话未听清,或理解不当),如果出现答非所问或者没听清楚，请指出问题，鼓励用户多说多练习,因为是对话，你生成的文字应尽量简短,不要包含md格式和其他特殊符号。'},
    # {'role':'system','content':'你是一个对话AI,目的是训练接受过人工耳蜗植入手术的用户更好地理解和使用中文。你应尽量使用简单通俗的语言对话，同时你要通过提问帮助用户练习听力和口语表达，判断他们对话沟通中出现的问题(如某处对话未听清,或理解不当),如果出现答非所问或者没听清楚，请指出问题，鼓励用户多说多练习,因为是对话，你生成的文字应尽量简短,不要包含md格式和其他特殊符号。'},
]

reports = {
    "id": index,
    "time": time.time(),
    "type": 0,
    "detail": []
}

init_dashscope_api_key()


class ChatManager():
    def __init__(self):
        self.chatting = 0

    def setChatting(self, status):
        self.chatting = status


def onSentenceEnd(text):
    print("Sentence ended:", text)
    chat_sentence = {'role': 'user', 'content': text}
    messages.append(chat_sentence)
    responses = dashscope.Generation.call(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
        api_key="sk-d239f644a54d4c109e494a6e3f6b7697",
        model="qwen-plus", # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=messages,
        result_format='message',
        )
    print("AI Response:", responses["output"]["choices"][0]["message"]["content"])
    messages.append(responses["output"]["choices"][0]["message"])
    global question_index
    r_item = {
        "id": question_index,
        "question": 0,
        "user_answer": text,
        "correct_answer":  responses["output"]["choices"][0]["message"]["content"],
        "result": 1
    }
    question_index += 1
    reports["detail"].append(r_item)
    with open(f"reports/{index}.json", "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=4)

    for client in list(server.clients):
        try:
            client.sendall(bytes("AI:" + responses["output"]["choices"][0]["message"]["content"] + "\n", "utf-8"))
        except:
            server.clients.remove(client)
    tts.send_text(responses["output"]["choices"][0]["message"]["content"])

def onResponse(text):
    print("ASR Response:", text)
    for client in list(server.clients):
        try:
            client.sendall(bytes(text + "\n", "utf-8"))
        except:
            server.clients.remove(client)


if __name__ == "__main__":
    chat = ChatManager()
    TTS_callback = TTS.TTSCallback(chat=chat)
    tts = TTS.TTSProcess(TTS_callback)
    tts.setup()
    ASR_callback = ASR.ASRCallback(on_response=onResponse, on_sentence_end=onSentenceEnd, chat=chat)
    asr = ASR.ASRProcess(ASR_callback)
    asr.start()
    tts.stop()