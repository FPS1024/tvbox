#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVBox 站点解析工具
从 tvbox_config.json 读取站点列表，获取每个站点的 JSON 配置
使用与 parse_api.py 相同的请求头，避免被标记为爬虫
"""

import requests
import json
import os
import sys
import time
from urllib.parse import quote

def get_tvbox_headers():
    """
    获取 TVBox 专用请求头，与 parse_api.py 保持一致
    """
    return {
        'User-Agent': 'okhttp/3.12.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }


def sanitize_filename(name):
    """
    清理文件名，移除或替换不安全的字符
    
    Args:
        name: 原始名称
        
    Returns:
        str: 清理后的文件名
    """
    # 移除或替换文件系统不支持的字符
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    # 移除首尾空格和点
    name = name.strip().strip('.')
    
    # 如果为空，使用默认名称
    if not name:
        name = 'unknown'
    
    return name


def fetch_site_config(api_url, site_name):
    """
    获取单个站点的配置
    
    Args:
        api_url: 站点 API 地址
        site_name: 站点名称（用于显示）
        
    Returns:
        dict: 站点配置，失败返回 None
    """
    headers = get_tvbox_headers()
    
    try:
        print(f"  正在获取: {site_name}...")
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 检查响应类型
        content_type = response.headers.get('Content-Type', '').lower()
        
        # 验证是否是 JSON
        if not (content_type.startswith('application/json') or 
                response.text.strip().startswith('{') or 
                response.text.strip().startswith('[')):
            print(f"    ⚠️  警告: 响应可能不是 JSON 格式")
        
        # 解析 JSON
        try:
            config = response.json()
            print(f"    ✅ 成功获取 ({len(response.text)} 字节)")
            return config
        except json.JSONDecodeError as e:
            print(f"    ❌ JSON 解析失败: {e}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"    ❌ 请求失败: {e}")
        return None
    except Exception as e:
        print(f"    ❌ 发生错误: {e}")
        return None


def save_site_config(config, filename, output_dir='sites'):
    """
    保存站点配置到文件
    
    Args:
        config: 站点配置字典
        filename: 文件名（不含扩展名）
        output_dir: 输出目录
        
    Returns:
        bool: 成功返回 True
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 清理文件名
    safe_filename = sanitize_filename(filename)
    filepath = os.path.join(output_dir, f"{safe_filename}.json")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"    ❌ 保存文件失败: {e}")
        return False


def parse_all_sites(config_file='tvbox_config.json', output_dir='sites', delay=0.5):
    """
    解析所有站点配置
    
    Args:
        config_file: TVBox 配置文件路径
        output_dir: 输出目录
        delay: 请求之间的延迟（秒），避免请求过快
        
    Returns:
        tuple: (成功数量, 失败数量, 总数)
    """
    # 读取配置文件
    if not os.path.exists(config_file):
        print(f"❌ 错误: 未找到 {config_file} 文件")
        print("请先运行 parse_api.py 生成配置文件")
        return (0, 0, 0)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return (0, 0, 0)
    
    # 获取站点列表
    sites = config.get('sites', [])
    
    if not sites:
        print("❌ 配置文件中没有找到站点")
        return (0, 0, 0)
    
    print(f"找到 {len(sites)} 个站点")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    
    # 遍历每个站点
    for i, site in enumerate(sites, 1):
        if not isinstance(site, dict):
            print(f"\n[{i}/{len(sites)}] ⚠️  跳过无效站点配置")
            fail_count += 1
            continue
        
        site_name = site.get('name', f'site_{i}')
        site_key = site.get('key', '')
        api_url = site.get('api', '')
        
        if not api_url:
            print(f"\n[{i}/{len(sites)}] ⚠️  {site_name}: 没有 API 地址，跳过")
            fail_count += 1
            continue
        
        print(f"\n[{i}/{len(sites)}] {site_name}")
        print(f"  API: {api_url}")
        
        # 获取站点配置
        site_config = fetch_site_config(api_url, site_name)
        
        if site_config:
            # 保存配置
            if save_site_config(site_config, site_name, output_dir):
                print(f"  ✅ 已保存: {output_dir}/{site_name}.json")
                success_count += 1
            else:
                fail_count += 1
        else:
            fail_count += 1
        
        # 延迟，避免请求过快
        if i < len(sites):
            time.sleep(delay)
    
    return (success_count, fail_count, len(sites))


def main():
    """主函数"""
    print("TVBox 站点配置解析工具")
    print("=" * 80)
    
    # 解析所有站点
    success, fail, total = parse_all_sites(
        config_file='tvbox_config.json',
        output_dir='sites',
        delay=0.5  # 每个请求之间延迟 0.5 秒
    )
    
    # 输出统计信息
    print("\n" + "=" * 80)
    print("解析完成！")
    print(f"  总数: {total}")
    print(f"  成功: {success}")
    print(f"  失败: {fail}")
    print(f"  成功率: {success/total*100:.1f}%" if total > 0 else "  成功率: 0%")
    print("=" * 80)
    
    if success > 0:
        print(f"\n✅ 所有站点配置已保存到 sites/ 目录")
        sys.exit(0)
    else:
        print("\n❌ 没有成功解析任何站点")
        sys.exit(1)


if __name__ == '__main__':
    main()

