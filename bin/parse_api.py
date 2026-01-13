#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVBox 接口解析工具
从 api-key.txt 读取接口地址，解析并保存为 tvbox_config.json
使用 TVBox 专用请求头，避免被标记为爬虫
"""

import requests
import json
import sys
import os

# 获取项目根目录（bin 目录的父目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def parse_tvbox_api(api_url):
    """
    解析 TVBox 接口，获取配置 JSON
    
    Args:
        api_url: TVBox 接口地址
        
    Returns:
        dict: 解析后的配置字典，失败返回 None
    """
    print(f"正在解析接口: {api_url}")
    print("-" * 80)
    
    # TVBox 专用请求头，避免被标记为爬虫
    headers = {
        'User-Agent': 'okhttp/3.12.0',  # TVBox Android 客户端使用的 User-Agent
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        # 发送请求
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 检查响应类型
        content_type = response.headers.get('Content-Type', '').lower()
        print(f"响应状态码: {response.status_code}")
        print(f"Content-Type: {content_type}")
        print(f"响应长度: {len(response.text)} 字节")
        
        # 验证是否是 JSON
        if not (content_type.startswith('application/json') or 
                response.text.strip().startswith('{') or 
                response.text.strip().startswith('[')):
            print("⚠️  警告: 响应可能不是 JSON 格式")
        
        # 解析 JSON
        try:
            config = response.json()
            print("✅ JSON 解析成功!")
            
            # 验证配置格式
            if isinstance(config, dict):
                sites_count = len(config.get('sites', []))
                lives_count = len(config.get('lives', []))
                print(f"✅ 配置验证通过:")
                print(f"   - 站点数量: {sites_count}")
                print(f"   - 直播源组数: {lives_count}")
                
                if sites_count == 0:
                    print("⚠️  警告: 未找到站点配置")
                
                return config
            elif isinstance(config, list):
                print(f"✅ 配置是列表格式，包含 {len(config)} 个元素")
                return config
            else:
                print("❌ 配置格式不正确")
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
            print(f"响应内容前500字符:\n{response.text[:500]}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return None


def save_config(config, output_file='tvbox_config.json'):
    """
    保存配置到 JSON 文件
    
    Args:
        config: 配置字典
        output_file: 输出文件路径（相对于项目根目录）
    """
    # 如果 output_file 不是绝对路径，则相对于项目根目录
    if not os.path.isabs(output_file):
        output_file = os.path.join(PROJECT_ROOT, output_file)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 配置已保存到: {output_file}")
        return True
    except Exception as e:
        print(f"❌ 保存配置失败: {e}")
        return False


def main():
    """主函数"""
    # 读取 API 地址（从项目根目录）
    api_key_file = os.path.join(PROJECT_ROOT, 'api-key.txt')
    
    if not os.path.exists(api_key_file):
        print(f"❌ 错误: 未找到 {api_key_file} 文件")
        print(f"请创建 {api_key_file} 文件，并在其中写入接口地址")
        sys.exit(1)
    
    try:
        with open(api_key_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        if not lines:
            print(f"❌ 错误: {api_key_file} 文件为空")
            sys.exit(1)
        
        # 使用第一行作为接口地址
        api_url = lines[0]
        print(f"从 {api_key_file} 读取接口地址: {api_url}\n")
        
    except Exception as e:
        print(f"❌ 读取 {api_key_file} 失败: {e}")
        sys.exit(1)
    
    # 解析接口
    config = parse_tvbox_api(api_url)
    
    if config:
        # 保存配置
        if save_config(config):
            print("\n" + "=" * 80)
            print("✅ 接口解析完成！")
            print("=" * 80)
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print("\n" + "=" * 80)
        print("❌ 接口解析失败")
        print("=" * 80)
        sys.exit(1)


if __name__ == '__main__':
    main()

