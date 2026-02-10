# For prerequisites running the following sample, visit https://help.aliyun.com/zh/model-studio/getting-started/first-api-call-to-qwen
import os
import signal  # for keyboard events handling (press "Ctrl+C" to terminate recording and translation)
import sys

import dashscope
import pyaudio
from dashscope.audio.asr import *

mic = None
streamInput = None

# Set recording parameters
sample_rate = 16000  # sampling rate (Hz)
channels = 1  # mono channel
dtype = 'int16'  # data type
format_pcm = 'pcm'  # the format of the audio data
block_size = 3200  # number of frames per buffer


def init_dashscope_api_key():
    """
        Set your DashScope API-key. More information:
        https://github.com/aliyun/alibabacloud-bailian-speech-demo/blob/master/PREREQUISITES.md
    """

    if 'DASHSCOPE_API_KEY' in os.environ:
        dashscope.api_key = os.environ[
            'DASHSCOPE_API_KEY']  # load API-key from environment variable DASHSCOPE_API_KEY
    else:
        dashscope.api_key = 'sk-05ea01424e5545c3b0e4a25b31e4ebd3'  # set API-key manually


class ASRProcess:
    def __init__(self, callback):
            # Create the translation callback
            self.callback = callback

            # Call self.recognition service by async mode, you can customize the self.recognition parameters, like model, format,
            # sample_rate For more information, please refer to https://help.aliyun.com/document_detail/2712536.html
            self.recognition = Recognition(
                model='paraformer-realtime-v2',
                # 'paraformer-realtime-v1'、'paraformer-realtime-8k-v1'
                format=format_pcm,
                # 'pcm'、'wav'、'opus'、'speex'、'aac'、'amr', you can check the supported formats in the document
                sample_rate=sample_rate,
                # support 8000, 16000
                semantic_punctuation_enabled=False,
                callback=self.callback)
            

    def signal_handler(self, sig, frame):
        print('Ctrl+C pressed, stop translation ...')
        # Stop translation
        self.recognition.stop()
        print('Translation stopped.')
        print(
            '[Metric] requestId: {}, first package delay ms: {}, last package delay ms: {}'
            .format(
                self.recognition.get_last_request_id(),
                self.recognition.get_first_package_delay(),
                self.recognition.get_last_package_delay(),
            ))
        # Forcefully exit the program
        sys.exit(0)

    def start(self):
        print('Initializing ...')

        # Start translation
        self.recognition.start()

        signal.signal(signal.SIGINT, self.signal_handler)
        print("Press 'Ctrl+C' to stop recording and translation...")
        # Create a keyboard listener until "Ctrl+C" is pressed

        if not streamInput:
            return

        while True:
            data = streamInput.read(3200, exception_on_overflow=False)
            if not self.callback.chat:
                self.recognition.send_audio_frame(data)
                continue
            if self.callback.chat.chatting == 0:
                self.recognition.send_audio_frame(data)
            else:
                continue

        self.recognition.stop()


# Real-time speech self.recognition callback
class ASRCallback(RecognitionCallback):
    def __init__(self, on_response=None, on_sentence_end=None, chat=None):
        super().__init__()
        self.on_response = on_response
        self.on_sentence_end = on_sentence_end
        self.chat = chat

    def on_open(self) -> None:
        global mic
        global streamInput
        print('self.recognitionCallback open.')
        mic = pyaudio.PyAudio()
        streamInput = mic.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=16000,
                          input=True)

    def on_close(self) -> None:
        global mic
        global streamInput
        print('self.recognitionCallback close.')
        streamInput.stop_stream()
        streamInput.close()
        mic.terminate()
        streamInput = None
        mic = None

    def on_complete(self) -> None:
        print('self.recognitionCallback completed.')  # translation completed

    def on_error(self, message) -> None:
        print('self.recognitionCallback task_id: ', message.request_id)
        print('self.recognitionCallback error: ', message.message)
        # Stop and close the audio stream if it is running
        if 'stream' in globals() and streamInput.active:
            streamInput.stop()
            streamInput.close()
        # Forcefully exit the program
        sys.exit(1)

    def on_event(self, result: RecognitionResult) -> None:
        sentence = result.get_sentence()
        if 'text' in sentence:
            if self.on_response:
                self.on_response(sentence['text'])
            print('self.recognitionCallback text: ', sentence['text'])
            if RecognitionResult.is_sentence_end(sentence):
                if self.chat:
                    self.chat.setChatting(1)
                if self.on_sentence_end:
                    self.on_sentence_end(sentence['text'])
                print(
                    'self.recognitionCallback sentence end, request_id:%s, usage:%s'
                    % (result.get_request_id(), result.get_usage(sentence)))


if __name__ == "__main__":
    init_dashscope_api_key()
    sr = ASRProcess(ASRCallback())
    sr.start()