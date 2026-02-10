#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将charset.txt文件中的汉字转换为U8g2正确的map文件格式
格式: 32-128,$4F60,$597D,$4E16,$754C
"""

import sys
import os

def txt_to_map(input_file, output_file):
    """
    将文本文件中的汉字转换为U8g2 map格式
    
    Args:
        input_file: 输入文件路径，包含汉字字符串（无换行）
        output_file: 输出文件路径，保存转换后的map格式
    """
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            print(f"警告: {input_file} 文件为空或仅包含空白字符")
            return
        
        # 去除重复字符（保持顺序）
        unique_chars = []
        seen = set()
        for char in content:
            if char not in seen:
                seen.add(char)
                unique_chars.append(char)
        
        print(f"读取到 {len(content)} 个字符，去重后剩 {len(unique_chars)} 个唯一字符")
        
        # 转换汉字为Unicode码点格式
        hex_codes = []
        for char in unique_chars:
            # 获取字符的Unicode码点
            code_point = ord(char)
            # 转换为4位十六进制（大写），前面加上$符号
            hex_code = f"${code_point:04X}"
            hex_codes.append(hex_code)
        
        # 构建完整的map文件内容
        # 格式: 32-128,$4F60,$597D,$4E16,$754C
        map_content = "32-128," + ",".join(hex_codes)
        
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(map_content)
        
        print(f"转换完成! 已生成 {output_file}")
        print(f"文件内容格式: 32-128 + {len(hex_codes)} 个汉字码点")
        
        # 显示前几个转换示例
        print("\n字符转换示例 (前10个):")
        for i, char in enumerate(unique_chars[:10]):
            hex_code = f"${ord(char):04X}"
            print(f"  '{char}' -> {hex_code}")
        
        # 显示map文件内容预览
        preview_length = min(80, len(map_content))
        preview = map_content[:preview_length]
        if len(map_content) > preview_length:
            preview += "..."
        print(f"\n生成的文件内容预览: {preview}")
        
        # 显示文件大小信息
        file_size = len(map_content)
        print(f"文件大小: {file_size} 字节")
            
    except FileNotFoundError:
        print(f"错误: 找不到输入文件 {input_file}")
    except Exception as e:
        print(f"转换过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

def validate_map_file(map_file):
    """
    验证生成的map文件格式是否正确
    """
    try:
        with open(map_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        print(f"\n验证 {map_file} 文件格式:")
        
        # 检查是否以"32-128,"开头
        if content.startswith("32-128,"):
            print("  ✓ 格式正确: 以 '32-128,' 开头")
        else:
            print("  ✗ 格式错误: 应以 '32-128,' 开头")
            return False
        
        # 分割内容检查
        parts = content.split(',')
        print(f"  ✓ 共 {len(parts)} 个部分")
        print(f"    第一部分: {parts[0]}")
        
        # 检查第二部分及之后的格式
        if len(parts) > 1:
            first_code = parts[1]
            if first_code.startswith('$') and len(first_code) == 5:
                print(f"  ✓ 汉字码点格式正确: {first_code}")
            else:
                print(f"  ✗ 汉字码点格式错误: {first_code}")
                return False
        
        # 检查所有码点格式
        for i, part in enumerate(parts[1:], 1):
            if not part.startswith('$') or len(part) != 5:
                print(f"  ✗ 第{i}个码点格式错误: {part}")
                return False
        
        print("  ✓ 所有码点格式正确")
        return True
        
    except Exception as e:
        print(f"验证失败: {e}")
        return False

def main():
    # 默认文件名
    input_filename = "charset.txt"
    output_filename = "chinese5.map"
    
    # 检查输入文件是否存在
    if not os.path.exists(input_filename):
        print(f"找不到输入文件: {input_filename}")
        print("请创建 charset.txt 文件并填入需要的汉字")
        print("\n文件内容格式要求:")
        print("  - 单行无换行的汉字字符串")
        print("  - 示例: '你好世界Arduino显示中文'")
        print("\n运行示例:")
        print("  1. echo '你好世界' > charset.txt")
        print("  2. python convert_to_map.py")
        return
    
    # 执行转换
    txt_to_map(input_filename, output_filename)
    
    # 验证生成的文件
    if os.path.exists(output_filename):
        validate_map_file(output_filename)
    
    # 显示下一步操作提示
    print("\n" + "="*60)
    print("下一步操作:")
    print(f"1. 将生成的 {output_filename} 文件复制到U8g2字体工具目录")
    print("   - 通常路径: U8g2/tools/font/build/")
    print("\n2. 使用bdfconv工具生成字体文件:")
    print("   cd /path/to/U8g2/tools/font/bdfconv/")
    print("   ./bdfconv -v ../bdf/unifont.bdf -b 0 -f 1 -M ../build/chinese.map -o my_font.c")
    print("\n3. 在Arduino/U8g2项目中使用生成的字体:")
    print("   u8g2.setFont(u8g2_font_unifont_t_chinese1);")
    print("   u8g2.print(\"你好世界\");")

def create_sample_files():
    """创建示例文件"""
    sample_text = "你好世界Arduino显示中文"
    
    # 创建示例charset.txt
    with open("charset_sample.txt", 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    print("已创建示例文件: charset_sample.txt")
    print(f"内容: {sample_text}")

if __name__ == "__main__":
    # 如果需要创建示例文件，取消下面的注释
    # create_sample_files()
    
    main()
