import json
import os

def load_chars_data():
    """加载汉字数据"""
    chars_file = 'practice/chars.json'
    try:
        with open(chars_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载数据失败: {e}")
        return []

def extract_chars(chars_data):
    """提取所有汉字"""
    all_chars = set()
    for item in chars_data:
        if 'chars' in item:
            all_chars.update(item['chars'])
    return sorted(all_chars)

def append_to_charset(chars):
    """将汉字追加到charset.txt"""
    charset_file = 'charset.txt'
    try:
        # 读取已有的汉字
        existing_chars = set()
        if os.path.exists(charset_file):
            with open(charset_file, 'r', encoding='utf-8') as f:
                existing_chars.update(f.read().strip())
        
        # 合并新汉字
        all_chars = existing_chars.union(chars)
        
        # 写入文件
        with open(charset_file, 'a', encoding='utf-8') as f:
            f.write(''.join(sorted(all_chars)))
        
        print(f"成功将 {len(chars)} 个新汉字追加到 {charset_file}")
        print(f"文件中共有 {len(all_chars)} 个汉字")
    except Exception as e:
        print(f"写入文件失败: {e}")

def main():
    """主函数"""
    print("开始从chars.json提取汉字并追加到charset.txt...")
    
    # 加载汉字数据
    chars_data = load_chars_data()
    if not chars_data:
        print("没有找到训练数据，退出程序。")
        return
    
    # 提取所有汉字
    all_chars = extract_chars(chars_data)
    print(f"从chars.json中提取到 {len(all_chars)} 个汉字")
    
    # 追加到charset.txt
    append_to_charset(all_chars)
    
    print("操作完成！")

if __name__ == "__main__":
    main()
