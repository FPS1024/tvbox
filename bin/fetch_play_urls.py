#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVBox 播放链接获取工具
从站点 JSON 文件中读取视频列表，通过 API 获取每个视频的播放链接
使用与 parse_api.py 相同的请求头，避免被标记为爬虫
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
    获取 TVBox 专用请求头，与 parse_api.py 保持一致
    """
    return {
        'User-Agent': 'okhttp/3.12.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }


def get_site_api_url(site_file):
    """
    从站点 JSON 文件名获取对应的 API URL
    
    Args:
        site_file: 站点 JSON 文件名（如 "ئەسىر16.json"）
        
    Returns:
        str: API URL，如果找不到返回 None
    """
    # 读取主配置文件（从项目根目录）
    config_file = os.path.join(PROJECT_ROOT, 'tvbox_config.json')
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        sites = config.get('sites', [])
        site_name = site_file.replace('.json', '')
        
        # 查找匹配的站点
        for site in sites:
            if site.get('name') == site_name:
                return site.get('api', '')
        
        return None
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return None


def fetch_vod_detail(api_url, vod_id):
    """
    获取视频详情（包含播放链接）
    
    Args:
        api_url: 站点 API 地址
        vod_id: 视频 ID
        
    Returns:
        dict: 视频详情，失败返回 None
    """
    headers = get_tvbox_headers()
    
    # 构建详情 API URL
    # 如果原 URL 已有参数，使用 &，否则使用 ?
    if '?' in api_url:
        detail_url = f"{api_url}&ac=detail&ids={vod_id}"
    else:
        detail_url = f"{api_url}?ac=detail&ids={vod_id}"
    
    try:
        response = requests.get(detail_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        # 检查返回格式
        if isinstance(data, dict) and 'list' in data and data['list']:
            return data['list'][0]  # 返回第一个视频详情
        
        return None
        
    except Exception as e:
        print(f"    ⚠️  获取详情失败 (vod_id={vod_id}): {e}")
        return None


def update_site_with_play_urls(site_file, site_dir='sites', delay=4.0):
    """
    更新站点 JSON 文件，为每个视频添加播放链接
    
    Args:
        site_file: 站点 JSON 文件名
        site_dir: 站点文件夹路径（相对于项目根目录）
        delay: 请求之间的延迟（秒）
        
    Returns:
        tuple: (成功数量, 失败数量, 总数)
    """
    # 如果 site_dir 不是绝对路径，则相对于项目根目录
    if not os.path.isabs(site_dir):
        site_dir = os.path.join(PROJECT_ROOT, site_dir)
    
    filepath = os.path.join(site_dir, site_file)
    
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return (0, 0, 0)
    
    # 读取站点配置
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            site_data = json.load(f)
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return (0, 0, 0)
    
    # 获取站点 API URL
    site_name = site_file.replace('.json', '')
    api_url = get_site_api_url(site_file)
    
    if not api_url:
        print(f"❌ 未找到站点 {site_name} 的 API 地址")
        return (0, 0, 0)
    
    print(f"\n处理站点: {site_name}")
    print(f"  API: {api_url}")
    
    # 获取视频列表
    video_list = site_data.get('list', [])
    
    if not video_list:
        print("  ⚠️  没有视频列表")
        return (0, 0, 0)
    
    print(f"  找到 {len(video_list)} 个视频")
    
    success_count = 0
    fail_count = 0
    
    # 遍历每个视频
    for i, video in enumerate(video_list, 1):
        if not isinstance(video, dict):
            continue
        
        vod_id = video.get('vod_id')
        vod_name = video.get('vod_name', '未知')
        
        if not vod_id:
            continue
        
        # 检查是否已有播放链接
        if 'vod_play_url' in video and video.get('vod_play_url'):
            print(f"  [{i}/{len(video_list)}] {vod_name[:30]}... (已有播放链接，跳过)")
            success_count += 1
            continue
        
        print(f"  [{i}/{len(video_list)}] {vod_name[:30]}...")
        
        # 获取视频详情
        detail = fetch_vod_detail(api_url, vod_id)
        
        if detail:
            # 更新播放链接信息
            if 'vod_play_from' in detail:
                video['vod_play_from'] = detail['vod_play_from']
            if 'vod_play_url' in detail:
                video['vod_play_url'] = detail['vod_play_url']
            if 'vod_content' in detail and detail.get('vod_content'):
                video['vod_content'] = detail['vod_content']
            if 'vod_actor' in detail:
                video['vod_actor'] = detail.get('vod_actor', '')
            if 'vod_director' in detail:
                video['vod_director'] = detail.get('vod_director', '')
            if 'vod_score' in detail:
                video['vod_score'] = detail.get('vod_score', '')
            
            success_count += 1
            print(f"    ✅ 已获取播放链接")
        else:
            fail_count += 1
            print(f"    ❌ 获取失败")
        
        # 延迟，避免请求过快
        if i < len(video_list):
            time.sleep(delay)
    
    # 保存更新后的文件
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(site_data, f, ensure_ascii=False, indent=2)
        print(f"\n  ✅ 文件已更新: {filepath}")
    except Exception as e:
        print(f"\n  ❌ 保存文件失败: {e}")
        return (0, 0, 0)
    
    return (success_count, fail_count, len(video_list))


def main():
    """主函数"""
    print("TVBox 播放链接获取工具")
    print("=" * 80)
    
    # 站点目录（项目根目录下的 sites 目录）
    site_dir = os.path.join(PROJECT_ROOT, 'sites')
    
    if not os.path.exists(site_dir):
        print(f"❌ 错误: 未找到 {site_dir} 文件夹")
        print("请先运行 parse_sites.py 生成站点配置文件")
        sys.exit(1)
    
    # 获取所有站点 JSON 文件
    site_files = [f for f in os.listdir(site_dir) if f.endswith('.json')]
    
    if not site_files:
        print(f"❌ 错误: {site_dir} 文件夹中没有 JSON 文件")
        sys.exit(1)
    
    print(f"找到 {len(site_files)} 个站点文件")
    print("=" * 80)
    
    total_success = 0
    total_fail = 0
    total_videos = 0
    
    # 处理每个站点
    for site_file in site_files:
        success, fail, total = update_site_with_play_urls(site_file, 'sites', delay=4.0)
        total_success += success
        total_fail += fail
        total_videos += total
    
    # 输出统计信息
    print("\n" + "=" * 80)
    print("处理完成！")
    print(f"  总视频数: {total_videos}")
    print(f"  成功: {total_success}")
    print(f"  失败: {total_fail}")
    if total_videos > 0:
        print(f"  成功率: {total_success/total_videos*100:.1f}%")
    print("=" * 80)
    
    if total_success > 0:
        print(f"\n✅ 所有播放链接已更新到站点 JSON 文件中")
        sys.exit(0)
    else:
        print("\n❌ 没有成功获取任何播放链接")
        sys.exit(1)


if __name__ == '__main__':
    main()

