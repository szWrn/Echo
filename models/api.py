import os
import dashscope

API_KEY = "sk-d239f644a54d4c109e494a6e3f6b7697"


def init_dashscope_api_key():
    """
        Set your DashScope API-key. More information:
        https://github.com/aliyun/alibabacloud-bailian-speech-demo/blob/master/PREREQUISITES.md
    """

    # if 'DASHSCOPE_API_KEY' in os.environ:
    #     dashscope.api_key = os.environ[
    #         'DASHSCOPE_API_KEY']  # load API-key from environment variable DASHSCOPE_API_KEY
    # else:
    #     dashscope.api_key = API_KEY  # set API-key manually
    dashscope.api_key = API_KEY  # set API-key manually