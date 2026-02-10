from Server import *
from models.api import init_dashscope_api_key
from models.ASR import ASRProcess, ASRCallback
from threading import Thread

HOST = "0.0.0.0"
PORT = 5001
server = Server(HOST, PORT)


def asr_callback(text):
    print("Send:", text[-20:])
    for client in list(server.clients):
        try:
            client.sendall(bytes(text[-20:] + "\n", "utf-8"))
            # client.sendall(b"Group2\n")
        except:
            server.clients.remove(client)


if __name__ == "__main__":
    t = Thread(target=server.run, daemon=True)
    t.start()
    init_dashscope_api_key()
    asr = ASRProcess(ASRCallback(on_response=asr_callback))
    asr.start()