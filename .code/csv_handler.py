"""
CSV处理模块 - 处理数据清洗和转换
"""
import pandas as pd
import re
import os
import json
from datetime import datetime, timedelta

def parse_pubdate(x):
    """解析发布日期"""
    if pd.isna(x):
        return ''
    x = str(x).strip()
    
    # 处理"几小时前""几天前"
    hour_match = re.match(r'(\d+)小时前', x)
    if hour_match:
        hours = int(hour_match.group(1))
        dt = datetime.now() - timedelta(hours=hours)
        return dt.strftime('%Y-%m-%d')
    
    day_match = re.match(r'(\d+)天前', x)
    if day_match:
        days = int(day_match.group(1))
        dt = datetime.now() - timedelta(days=days)
        return dt.strftime('%Y-%m-%d')
    
    # 处理"MM-DD"格式
    md_match = re.match(r'^(\d{1,2})-(\d{1,2})$', x)
    if md_match:
        month, day = md_match.groups()
        year = datetime.now().year
        try:
            dt = datetime(year, int(month), int(day))
            if dt > datetime.now():
                dt = datetime(year-1, int(month), int(day))
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return x
    
    # 处理标准日期格式
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M:%S'):
        try:
            dt = datetime.strptime(x, fmt)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            continue
    
    # 处理"昨天""前天"
    if x == '昨天':
        dt = datetime.now() - timedelta(days=1)
        return dt.strftime('%Y-%m-%d')
    if x == '前天':
        dt = datetime.now() - timedelta(days=2)
        return dt.strftime('%Y-%m-%d')
    
    # 处理"X月X日"
    md2_match = re.match(r'^(\d{1,2})月(\d{1,2})日$', x)
    if md2_match:
        month, day = md2_match.groups()
        year = datetime.now().year
        try:
            dt = datetime(year, int(month), int(day))
            if dt > datetime.now():
                dt = datetime(year-1, int(month), int(day))
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return x
    
    return x

def process_csv_data(df: pd.DataFrame, blacklist_path=None) -> pd.DataFrame:
    """
    处理CSV数据
    :param df: 原始数据DataFrame
    :param blacklist_path: 黑名单JSON文件路径
    :return: 处理后的DataFrame
    """
    # 1. 将duration列转换为秒数
    df['duration'] = df['duration'].apply(
        lambda x: sum(int(i) * 60 ** idx for idx, i in enumerate(reversed(x.split(':')))) if isinstance(x, str) else x
    )

    # 2. 将danmu列统一单位（删去万）
    df['danmu'] = df['danmu'].apply(
        lambda x: int(float(x.replace('万', '').replace(' ', '')) * 10000) if '万' in x else int(float(x.replace(' ', '')))
    )
    
    # 3. 将views列统一单位（删去万）
    df['views'] = df['views'].apply(
        lambda x: float(x.replace('万', '').replace(' ', '')) if '万' in x else float(x.replace(' ', ''))
    )
    
    # 4. 统一pubdate的日期
    df['pubdate'] = df['pubdate'].apply(parse_pubdate)

    # 5. 通过黑名单剔除相关视频
    if blacklist_path is None:
        blacklist_path = os.path.join(os.path.dirname(__file__), 'black_list.json')
    
    if os.path.exists(blacklist_path):
        with open(blacklist_path, 'r', encoding='utf-8') as f:
            black_data = json.load(f)
        
        # 支持新的JSON格式，提取blacklist字段
        if isinstance(black_data, dict) and 'blacklist' in black_data:
            black_list = black_data['blacklist']
        else:
            black_list = black_data
        
        if isinstance(black_list, list) and len(black_list) > 0:
            # bvid/aid黑名单
            if isinstance(black_list[0], str):
                if 'bvid' in df.columns:
                    df = df[~df['bvid'].isin(black_list)]
                elif 'aid' in df.columns:
                    df = df[~df['aid'].isin(black_list)]
            # 标题+日期黑名单
            elif isinstance(black_list[0], dict):
                bl_set = set((item.get('title',''), item.get('pubdate','')) for item in black_list)
                if 'title' in df.columns and 'pubdate' in df.columns:
                    df = df[~df.apply(lambda row: (row['title'], row['pubdate']) in bl_set, axis=1)]

    return df

def load_csv(csv_file: str) -> pd.DataFrame:
    """读取CSV文件"""
    return pd.read_csv(csv_file, encoding='utf-8-sig')

def save_csv(df: pd.DataFrame, csv_file: str) -> None:
    """保存CSV文件"""
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')

def json_to_csv(json_file: str, csv_file: str):
    """JSON转CSV"""
    df = pd.read_json(json_file, encoding='utf-8')
    save_csv(df, csv_file)
    return csv_file
