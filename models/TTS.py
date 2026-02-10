import base64
import os
import threading
import dashscope
import pyaudio
from dashscope.audio.qwen_tts_realtime import *

qwen_tts_realtime: QwenTtsRealtime = None

player = pyaudio.PyAudio()
streamOutput = player.open(format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True)

DO_VIDEO_TEST = False

def init_dashscope_api_key():
    """
        Set your DashScope API-key. More information:
        https://github.com/aliyun/alibabacloud-bailian-speech-demo/blob/master/PREREQUISITES.md
    """

    # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
    if 'DASHSCOPE_API_KEY' in os.environ:
        dashscope.api_key = os.environ[
            'DASHSCOPE_API_KEY']  # load API-key from environment variable DASHSCOPE_API_KEY
    else:
        dashscope.api_key = 'sk-05ea01424e5545c3b0e4a25b31e4ebd3'  # set API-key manually


class TTSProcess():
    def __init__(self, callback):
        # Create the translation callback
        self.callback = callback

        self.qwen_tts_realtime = QwenTtsRealtime(
            model='qwen3-tts-flash-realtime',
            callback=callback,
            # 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime
            url='wss://dashscope.aliyuncs.com/api-ws/v1/realtime'
            )
        
    def setup(self):
        self.qwen_tts_realtime.connect()
        self.qwen_tts_realtime.update_session(
            voice = 'Cherry',
            response_format = AudioFormat.PCM_24000HZ_MONO_16BIT,
            mode = 'commit'        
        )

    def send_text(self, text):
        self.qwen_tts_realtime.append_text(text)
        self.qwen_tts_realtime.commit()
        self.callback.wait_for_response_done()
        self.callback.reset_event()

    def stop(self):
        self.qwen_tts_realtime.finish()


class TTSCallback(QwenTtsRealtimeCallback):
    def __init__(self, on_response=None, chat=None):
        super().__init__()
        self.response_counter = 0
        self.complete_event = threading.Event()
        self.on_response = on_response
        self.chat = chat

    def reset_event(self):
        self.response_counter += 1
        self.complete_event = threading.Event()
        if self.chat:
            self.chat.chatting = 0

    def on_open(self) -> None:
        print('connection opened, init player')

    def on_close(self, close_status_code, close_msg) -> None:
        print('connection closed with code: {}, msg: {}, destroy player'.format(close_status_code, close_msg))

    def on_event(self, response: str) -> None:
        try:
            type = response['type']
            if 'session.created' == type:
                print('start session: {}'.format(response['session']['id']))
            if 'response.audio.delta' == type:
                recv_audio_b64 = response['delta']
                sound_frame = base64.b64decode(recv_audio_b64)
                streamOutput.write(sound_frame)
                if self.on_response:
                    self.on_response(sound_frame)
            if 'response.done' == type:
                self.complete_event.set()
            if 'session.finished' == type:
                print('session finished')
                self.complete_event.set()
        except Exception as e:
            print('[Error] {}'.format(e))
            return

    def wait_for_response_done(self):
        self.complete_event.wait()


if __name__  == '__main__':
    init_dashscope_api_key()

    print('Initializing ...')

    tts = TTSProcess(TTSCallback())
    tts.setup()
    tts.send_text('你好，欢迎使用DashScope实时文本到语音合成服务。')
    tts.stop()
