#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""共享模块 - 版本管理 + 进度条 + 场景关键词提取"""

import os
import sys
import re
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_BASE = os.path.join(PROJECT_DIR, '知识库')
VERSION_FILE = os.path.join(OUTPUT_BASE, '.version')

def get_current_version():
    os.makedirs(OUTPUT_BASE, exist_ok=True)
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as f:
            return int(f.read().strip())
    return 0

def bump_version():
    v = get_current_version() + 1
    os.makedirs(OUTPUT_BASE, exist_ok=True)
    with open(VERSION_FILE, 'w') as f:
        f.write(str(v))
    return v

def get_output_dir(bump=False):
    if bump:
        v = bump_version()
    else:
        v = get_current_version()
        if v == 0:
            v = bump_version()
    out_dir = os.path.join(OUTPUT_BASE, f'v{v}')
    os.makedirs(out_dir, exist_ok=True)
    return out_dir, v

def write_file(filepath, lines):
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

def progress_bar(iterable, desc='Processing', total=None):
    if total is None:
        total = len(iterable) if hasattr(iterable, '__len__') else None
    start_time = time.time()
    for i, item in enumerate(iterable, 1):
        yield item
        if i % 1000 == 0 or (total and i == total):
            elapsed = time.time() - start_time
            if total:
                pct = i / total * 100
                rate = i / elapsed if elapsed > 0 else 0
                eta = (total - i) / rate if rate > 0 else 0
                sys.stderr.write(f'\r{desc}: {i}/{total} ({pct:.1f}%) | {rate:.0f} it/s | ETA {eta:.0f}s')
            else:
                sys.stderr.write(f'\r{desc}: {i} | {elapsed:.0f}s')
            sys.stderr.flush()
    sys.stderr.write('\n')
    sys.stderr.flush()

# 场景关键词映射
SCENE_KEYWORDS = {
    '教室': '教室', '学校': '校园', '校服': '校园', '上课': '教室', '课堂': '教室',
    '卧室': '卧室', '起床': '卧室', '床': '卧室', '睡': '卧室',
    '浴室': '浴室', '洗澡': '浴室', '沐浴': '浴室', '淋浴': '浴室', '泡澡': '浴室',
    '海滩': '海滩', '海边': '海滩', '沙滩': '海滩', '泳装': '泳池', '泳池': '泳池',
    '森林': '森林', '树林': '森林', '树': '户外', '花': '花田', '花田': '花田',
    '城市': '城市', '街': '街道', '夜景': '夜景', '夜晚': '夜景', '霓虹': '夜景',
    '咖啡': '咖啡厅', '咖啡馆': '咖啡厅', '餐厅': '餐厅', '吃饭': '餐厅',
    '夕阳': '夕阳', '黄昏': '夕阳', '日落': '夕阳', '傍晚': '夕阳',
    '樱花': '樱花', '樱': '樱花', '春天': '春季',
    '雨': '雨天', '下雨': '雨天', '雪': '雪景', '下雪': '雪景', '冬天': '冬季',
    '夏天': '夏季', '秋天': '秋季', '枫': '秋季', '红叶': '秋季',
    '公园': '公园', '庭院': '庭院', '花园': '花园', '和室': '和室',
    '图书馆': '图书馆', '书店': '书店', '办公室': '办公室',
    '水': '水边', '河': '河边', '湖': '湖边', '海': '海边',
    '天空': '天空', '云': '天空', '星空': '星空', '月': '夜景',
    '乐器': '音乐', '演奏': '音乐', '吉他': '音乐', '钢琴': '音乐',
    '运动': '运动', '跑步': '运动', '游泳': '运动', '战斗': '战斗',
    '猫': '动物', '狗': '动物', '兽耳': '兽耳',
    '和服': '和风', '巫女': '巫女', '神社': '神社',
    '角色扮演': '角色扮演', 'cosplay': '角色扮演',
    '室内': '室内', '室外': '户外', '户外': '户外', '野外': '户外',
}

SCENE_FALLBACK = [
    (r'(坐在|站在|躺在|靠着|倚在).{0,5}(教室|学校|课桌|讲台)', '教室'),
    (r'(坐在|躺在|睡在).{0,3}(床|沙发|被窝)', '卧室'),
    (r'(走进|来到|站在).{0,3}(浴室|浴缸|淋浴)', '浴室'),
    (r'(走在|站在|穿过).{0,3}(森林|树林|林间)', '森林'),
    (r'(走在|站在|穿过).{0,3}(街|城市|街道|霓虹)', '街道'),
    (r'(雨|下雨|倾盆|淅沥|雨滴)', '雨天'),
    (r'(雪|飘雪|白雪|积雪|雪花)', '雪景'),
    (r'(樱花|飘落的花瓣|花海|花田)', '樱花'),
    (r'(夕阳|落日|黄昏|晚霞|余晖)', '夕阳'),
    (r'(夜晚|深夜|星空|月亮|月光|霓虹)', '夜景'),
    (r'(教室|课堂|课桌|讲台|黑板)', '教室'),
    (r'(海边|海滩|沙滩|海浪)', '海滩'),
    (r'(神社|鸟居|巫女|和风)', '神社'),
    (r'(咖啡厅|咖啡馆|咖啡|拿铁)', '咖啡厅'),
    (r'(花园|庭院|公园|草地|草坪)', '花园'),
    (r'(和室|榻榻米|日式房间)', '和室'),
    (r'(泳池|游泳池|游泳|水上)', '泳池'),
    (r'(餐厅|饭店|吃饭|餐桌)', '餐厅'),
    (r'(图书馆|书架|读书)', '图书馆'),
    (r'(天空|蓝天|白云|晴朗)', '天空'),
    (r'(运动|跑步|健身|训练)', '运动'),
    (r'(战斗|战场|武器|剑|枪)', '战斗'),
    (r'(水边|湖边|河边|溪流|池塘)', '水边'),
]

def extract_scene(text):
    text_lower = text.lower()
    for kw, scene in SCENE_KEYWORDS.items():
        if kw.lower() in text_lower:
            return scene
    for pattern, scene in SCENE_FALLBACK:
        if re.search(pattern, text):
            return scene
    words = text.replace(',', ' ').replace('，', ' ').split()
    for i, w in enumerate(words):
        if len(w) >= 3 and w in SCENE_KEYWORDS:
            return SCENE_KEYWORDS[w]
    return text[:15].strip() + '...'
