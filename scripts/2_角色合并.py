#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2_角色合并.py - 角色中文化（animadex + e261 补中文名）"""

import csv
import json
import os
import sys
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
from _common import get_output_dir, write_file, progress_bar

SOURCE_DIR = os.path.join(PROJECT_DIR, 'source')
ANIMADEX_JSON = os.path.join(SOURCE_DIR, 'animadex_index.csv')
E261_CSV = os.path.join(SOURCE_DIR, 'danbooru_e261_updated.csv')

def load_e261_char_dict():
    cdict = {}
    with open(E261_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 3:
                continue
            eng, chn, cat = row[0], row[1], row[2]
            if cat == '二次元角色':
                cdict[eng.strip()] = chn.strip()
    print(f'[INFO] e261 角色词典: {len(cdict)} 条目')
    return cdict

def parse_animadex():
    chars = []
    with open(ANIMADEX_JSON, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except:
                continue
            if obj.get('source_kind') != 'character':
                continue
            tag_raw = obj.get('tag', '').replace('\\', '')
            trigger_raw = obj.get('trigger', '').replace('\\', '')
            char_tag = tag_raw.split(',')[0].strip()
            chars.append({
                'char_tag': char_tag,
                'name': obj.get('name', ''),
                'series': obj.get('copyright_name', 'original'),
                'trigger': trigger_raw,
                'tags': obj.get('tags', [])
            })
    print(f'[INFO] Animadex 角色: {len(chars)}')
    return chars

def match_chinese(chars, cdict):
    matched = 0
    for c in chars:
        ct = c['char_tag']
        if ct in cdict:
            c['chinese'] = cdict[ct]
            matched += 1
            continue
        ct_underscore = ct.replace(' ', '_')
        if ct_underscore in cdict:
            c['chinese'] = cdict[ct_underscore]
            matched += 1
            continue
        stripped = re.sub(r'[_\s]*\([^)]*\)', '', ct)
        if stripped and stripped in cdict:
            c['chinese'] = cdict[stripped]
            matched += 1
            continue
        stripped_us = stripped.replace(' ', '_')
        if stripped_us and stripped_us in cdict:
            c['chinese'] = cdict[stripped_us]
            matched += 1
            continue
        c['chinese'] = ''
    print(f'[匹配] 中文名: {matched}/{len(chars)} ({matched/len(chars)*100:.1f}%)')
    return chars

def main():
    out_dir, version = get_output_dir()
    print(f'\n=== 2_角色合并.py ===')
    print(f'输出目录: {out_dir} (v{version})\n')
    
    cdict = load_e261_char_dict()
    chars = parse_animadex()
    chars = match_chinese(chars, cdict)
    
    lines = []
    for i, c in enumerate(chars):
        tags_str = ', '.join(c['tags'])
        chinese = c.get('chinese', '')
        name = c.get('name', c['char_tag'])
        lines.append(f"[DOMAIN:角色] [CAT:{c['series']}]")
        lines.append(f"name: {name}")
        lines.append(f"trigger: {c['trigger']}")
        if chinese:
            lines.append(f"chinese: {chinese}")
        lines.append(f"tags: {tags_str}")
        if i < len(chars) - 1:
            lines.append('---')
    
    out_file = os.path.join(out_dir, 'characters_merged.txt')
    write_file(out_file, lines)
    print(f'\n输出: characters_merged.txt ({len(lines)} 行)')

if __name__ == '__main__':
    main()
