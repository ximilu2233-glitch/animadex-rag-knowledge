#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""4_prompt_prep.py - 提示词示例预处理（去重+场景提取）"""

import csv
import os
import sys
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
from _common import get_output_dir, write_file, progress_bar, extract_scene

SOURCE_DIR = os.path.join(PROJECT_DIR, 'source')
PROMPT_CSV = os.path.join(SOURCE_DIR, '1万条提示词完整版.csv')

def main():
    out_dir, version = get_output_dir()
    print(f'\n=== 4_prompt_prep.py ===')
    print(f'输出目录: {out_dir} (v{version})\n')
    
    seen = set()
    lines = []
    total = 0
    duplicates = 0
    
    with open(PROMPT_CSV, 'r', encoding='utf-8') as f:
        for row in f:
            total += 1
            text = row.strip()
            if not text or len(text) < 10:
                continue
            key = text[:100]
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
            scene = extract_scene(text)
            lines.append(f'[DOMAIN:提示词] [CAT:{scene}] {text}')
    
    print(f'[统计] 总计: {total}, 去重后: {len(lines)}, 去重: {duplicates}')
    print(f'[场景] 分布:')
    scene_count = {}
    for line in lines:
        m = re.match(r'\[DOMAIN:提示词\] \[CAT:(.+?)\]', line)
        if m:
            cat = m.group(1)
            scene_count[cat] = scene_count.get(cat, 0) + 1
    for cat, cnt in sorted(scene_count.items(), key=lambda x: -x[1]):
        print(f'  {cat}: {cnt}')
    
    out_file = os.path.join(out_dir, 'prompt_examples.txt')
    write_file(out_file, lines)
    print(f'\n输出: prompt_examples.txt ({len(lines)} 行)')

if __name__ == '__main__':
    main()
