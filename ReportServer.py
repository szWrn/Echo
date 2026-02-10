from flask import Flask, jsonify, request
import os
import json

app = Flask(__name__)

@app.route('/get_index/')
def get_index():
    reports_dir = 'reports'
    all_data = []
    
    # 获取所有JSON文件并按文件名数字排序
    json_files = []
    for file_name in os.listdir(reports_dir):
        if file_name.endswith('.json'):
            try:
                # 提取文件名中的数字部分
                file_num = int(file_name.split('.')[0])
                json_files.append((file_num, file_name))
            except ValueError:
                pass
    
    # 按数字顺序排序
    json_files.sort(key=lambda x: x[0])
    
    # 读取并处理所有文件的数据
    for _, file_name in json_files:
        file_path = os.path.join(reports_dir, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # 提取需要的字段：id, time, type
                    # 注意：这里假设每个文件对应一个训练记录
                    # 从文件名中获取id
                    try:
                        training_id = int(file_name.split('.')[0])
                    except ValueError:
                        continue
                    
                    # 构建训练记录
                    training_record = {
                        'id': training_id,
                        'time': data.get('time', ''),
                        'type': data.get('type', 0)  # 从数据中获取类型
                    }
                    all_data.append(training_record)
        except Exception as e:
            pass
    
    return jsonify({"data": all_data})

@app.route('/get_report/', methods=['POST'])
def get_report():
    # 获取请求体中的id
    try:
        request_data = request.get_json()
        training_id = request_data.get('id')
        if not training_id:
            return jsonify({"data": []})
        
        training_id = int(training_id)
    except Exception:
        return jsonify({"data": []})
    
    reports_dir = 'reports'
    report_data = []
    training_type = 0  # 默认类型
    
    # 首先获取训练类型
    # 读取所有文件查找对应id的训练类型
    json_files = []
    for file_name in os.listdir(reports_dir):
        if file_name.endswith('.json'):
            try:
                file_num = int(file_name.split('.')[0])
                json_files.append((file_num, file_name))
            except ValueError:
                pass
    
    json_files.sort(key=lambda x: x[0])
    
    # 查找对应id的文件
    target_file = None
    for file_num, file_name in json_files:
        if file_num == training_id:
            target_file = file_name
            break
    
    if not target_file:
        return jsonify({"data": []})
    
    # 读取目标文件
    file_path = os.path.join(reports_dir, target_file)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                # 获取训练类型
                training_type = data.get('type', 0)
                
                if 'detail' in data:
                    # 处理detail数据
                    for item in data['detail']:
                        # 构建报告项
                        report_item = {
                            "question": item.get('question', ''),  # 修正字段名为question
                            "user_answer": item.get('user_answer', ''),
                            "correct_answer": item.get('correct_answer', ''),
                            "result": item.get('result', 0)  # 修正字段名为result
                        }
                        
                        # # 根据训练类型调整返回格式
                        # if training_type == 0:  # 人机对话训练
                        #     # user_answer -> 用户对话
                        #     # correct_answer -> AI对话
                        #     # 其余为空字符串
                        #     report_item = {
                        #         "question": "",
                        #         "user_answer": report_item.get('user_answer', ''),
                        #         "correct_answer": report_item.get('correct_answer', ''),
                        #         "result": 0  # 人机对话不关注结果
                        #     }
                        # elif training_type == 2:  # 听声辩位
                        #     # question -> 空字符串省略
                        #     report_item.pop('question', None)
                        
                        report_data.append(report_item)
    except Exception as e:
        pass
    
    return jsonify({"data": report_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443)
