#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVBox 站点完整数据获取工具
从 sites 目录下的某个 JSON 文件读取第一页数据，获取所有页面的数据并合并
"""

import requests
import json
import os
import sys
import time
from urllib.parse import urlparse, parse_qs, urlencode

# 获取项目根目录（bin 目录的父目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)


def get_tvbox_headers():
    """
    获取 TVBox 专用请求头，与其他脚本保持一致
    """
    return {
        'User-Agent': 'okhttp/3.12.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }


def get_site_api_url(site_name):
    """
    从站点名称获取对应的 API URL
    
    Args:
        site_name: 站点名称（如 "ئەسىر"）
        
    Returns:
        str: API URL，如果找不到返回 None
    """
    # 读取主配置文件（从项目根目录）
    config_file = os.path.join(PROJECT_ROOT, 'tvbox_config.json')
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        sites = config.get('sites', [])
        
        # 查找匹配的站点
        for site in sites:
            if site.get('name') == site_name:
                return site.get('api', '')
        
        return None
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return None


def fetch_page(api_url, page=1):
    """
    获取指定页面的数据
    
    Args:
        api_url: 站点 API 地址
        page: 页码（从1开始）
        
    Returns:
        dict: 页面数据，失败返回 None
    """
    headers = get_tvbox_headers()
    
    # 构建分页 API URL
    # 如果原 URL 已有参数，使用 &，否则使用 ?
    if '?' in api_url:
        page_url = f"{api_url}&pg={page}"
    else:
        page_url = f"{api_url}?pg={page}"
    
    try:
        response = requests.get(page_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 解析 JSON
        data = response.json()
        return data
        
    except Exception as e:
        print(f"    ⚠️  获取第 {page} 页失败: {e}")
        return None


def fetch_all_pages(site_file, delay=3.0):
    """
    获取站点的所有页面数据并合并
    
    Args:
        site_file: 站点 JSON 文件名（如 "ئەسىر.json"）
        delay: 请求之间的延迟（秒）
        
    Returns:
        dict: 合并后的完整数据，失败返回 None
    """
    # 站点目录（项目根目录下的 sites 目录）
    site_dir = os.path.join(PROJECT_ROOT, 'sites')
    filepath = os.path.join(site_dir, site_file)
    
    if not os.path.exists(filepath):
        print(f"❌ 错误: 未找到文件 {filepath}")
        return None
    
    # 读取第一页数据
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_page_data = json.load(f)
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None
    
    # 获取站点名称和 API URL
    site_name = site_file.replace('.json', '')
    api_url = get_site_api_url(site_name)
    
    if not api_url:
        print(f"❌ 未找到站点 {site_name} 的 API 地址")
        return None
    
    # 获取总页数
    pagecount = first_page_data.get('pagecount', 1)
    current_page = first_page_data.get('page', 1)
    
    print(f"\n处理站点: {site_name}")
    print(f"  API: {api_url}")
    print(f"  当前页: {current_page}")
    print(f"  总页数: {pagecount}")
    print(f"  第一页视频数: {len(first_page_data.get('list', []))}")
    print("=" * 80)
    
    # 如果只有一页，直接返回
    if pagecount <= 1:
        print("  只有一页数据，无需获取更多页面")
        return first_page_data
    
    # 合并所有页面的视频列表
    all_videos = first_page_data.get('list', []).copy()
    
    # 获取剩余页面
    for page in range(2, pagecount + 1):
        print(f"\n  正在获取第 {page}/{pagecount} 页...")
        
        page_data = fetch_page(api_url, page)
        
        if page_data:
            page_videos = page_data.get('list', [])
            if page_videos:
                all_videos.extend(page_videos)
                print(f"    ✅ 成功获取 {len(page_videos)} 个视频")
            else:
                print(f"    ⚠️  第 {page} 页没有视频数据")
        else:
            print(f"    ❌ 第 {page} 页获取失败")
        
        # 延迟，避免请求过快
        if page < pagecount:
            time.sleep(delay)
    
    # 构建完整的数据结构
    complete_data = first_page_data.copy()
    complete_data['list'] = all_videos
    complete_data['page'] = 1  # 保持为第一页
    complete_data['total'] = len(all_videos)  # 更新总数为实际获取的数量
    
    print("\n" + "=" * 80)
    print(f"✅ 数据获取完成！")
    print(f"  总页数: {pagecount}")
    print(f"  总视频数: {len(all_videos)}")
    print("=" * 80)
    
    return complete_data


def save_complete_data(data, site_file):
    """
    保存完整数据到文件
    
    Args:
        data: 完整的数据字典
        site_file: 站点 JSON 文件名
        
    Returns:
        bool: 成功返回 True
    """
    # 站点目录（项目根目录下的 sites 目录）
    site_dir = os.path.join(PROJECT_ROOT, 'sites')
    filepath = os.path.join(site_dir, site_file)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 完整数据已保存到: {filepath}")
        return True
    except Exception as e:
        print(f"\n❌ 保存文件失败: {e}")
        return False


def main():
    """主函数"""
    print("TVBox 站点完整数据获取工具")
    print("=" * 80)
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python fetch_all_pages.py <站点文件名>")
        print("示例: python fetch_all_pages.py ئەسىر.json")
        sys.exit(1)
    
    site_file = sys.argv[1]
    
    # 确保文件名以 .json 结尾
    if not site_file.endswith('.json'):
        site_file += '.json'
    
    # 获取所有页面数据
    complete_data = fetch_all_pages(site_file, delay=3.0)
    
    if complete_data:
        # 保存完整数据
        if save_complete_data(complete_data, site_file):
            print("\n" + "=" * 80)
            print("✅ 处理完成！")
            print("=" * 80)
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print("\n" + "=" * 80)
        print("❌ 处理失败")
        print("=" * 80)
        sys.exit(1)


if __name__ == '__main__':
    main()

