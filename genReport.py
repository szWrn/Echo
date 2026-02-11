from models.api import init_dashscope_api_key
import dashscope
import json

message = [
    {"role": "system", "content": "你是一个人工耳蜗术后康复训练系统报告生成AI,你将接受一份用户训练记录的json文件,并根据训练记录生成一个去除文件头的html格式康复报告,不要写文件头!!!!内容不要太长,训练记录包含一个type字段,该字段为训练类型,(0:人机对话训练，1:听音辩声，2:听声辩位)，报告包括四个部分：等级与分数，题目统计（对话不需要此部分），薄弱项分析，结语，你的输出不应包含除报告以外的任何内容"},
    {"role": "system", "content": ""}
]


init_dashscope_api_key()
with open("reports/index.txt", "r", encoding="utf-8") as f:
    index = int(f.read().strip())
    f.close()
for i in range(index):
    print(f"正在生成第{i}条报告")
    with open(f"reports/{i}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        data_str = json.dumps(data, ensure_ascii=False, indent=4)
        f.close()
    message[1]["content"] = data_str
    responses = dashscope.Generation.call(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
        api_key="sk-d239f644a54d4c109e494a6e3f6b7697",
        model="qwen-plus", # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=message,
        result_format='message'
        )
    data["report"] = responses["output"]["choices"][0]["message"]["content"]
    with open(f"reports/{i}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.close()