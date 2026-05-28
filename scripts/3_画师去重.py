#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""3_画师去重.py - 画师合并去重 + 精选画师 template 生成"""

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
ARTISTS_CSV = os.path.join(SOURCE_DIR, 'artists.csv')
CURATED_MD = os.path.join(SOURCE_DIR, '画师精选.md')

def parse_animadex_artists():
    artists = {}
    with open(ANIMADEX_JSON, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except:
                continue
            if obj.get('source_kind') != 'artist':
                continue
            tag = obj.get('tag', '').replace('\\', '').strip()
            if not tag or tag in ('banned artist', 'banned_artist'):
                continue
            artists[tag] = {
                'tag': tag,
                'name': obj.get('name', ''),
                'works': obj.get('works', 0)
            }
    print(f'[INFO] Animadex 画师: {len(artists)}')
    return artists

def parse_artists_csv():
    artists = {}
    with open(ARTISTS_CSV, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except:
                continue
            tag = obj.get('tag', '').replace('\\', '').strip()
            if not tag or tag in ('banned artist', 'banned_artist'):
                continue
            artists[tag] = {
                'tag': tag,
                'name': '',
                'works': obj.get('works', 0),
                'uniqueness': obj.get('uniqueness_score', 0)
            }
    print(f'[INFO] Artists CSV 画师: {len(artists)}')
    return artists

def parse_curated():
    curated = {}
    current_cat = ''
    with open(CURATED_MD, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('[CAT:'):
                current_cat = line[5:].rstrip(']')
            elif line.startswith('@'):
                m = re.match(r'@(\S+)', line)
                if not m:
                    continue
                tag = m.group(1)
                rest = line[len(tag)+1:].strip()
                name = ''
                style = ''
                if rest.startswith(':'):
                    rest = rest[1:].strip()
                n_match = re.match(r'\(([^)]+)\)', rest)
                if n_match:
                    name = n_match.group(1)
                    style = rest[n_match.end():].strip()
                else:
                    style = rest
                curated[tag] = {
                    'tag': tag,
                    'name': name,
                    'style': style,
                    'category': current_cat
                }
    print(f'[INFO] 精选画师: {len(curated)}')
    return curated

def generate_artist_template(tag, style_desc):
    """从风格描述生成英文模板标签"""
    style_lower = style_desc.lower()
    templates = []
    if '格子' in style_desc or 'plaid' in style_lower:
        templates.append('plaid pattern')
    if '清新' in style_desc or 'pastel' in style_lower or '柔和' in style_desc:
        templates.append('pastel colors')
        templates.append('soft shading')
    if '光影' in style_desc or 'lighting' in style_lower or '高光' in style_desc:
        templates.append('cinematic lighting')
    if '校园' in style_desc or 'school' in style_lower:
        templates.append('school theme')
    if '日常' in style_desc or 'casual' in style_lower:
        templates.append('casual')
    if '黑长直' in style_desc:
        templates.append('black hair')
        templates.append('long hair')
    if '女仆' in style_desc or 'maid' in style_lower:
        templates.append('maid headdress')
        templates.append('apron')
    if '大场景' in style_desc or '背景' in style_desc or 'scenic' in style_lower:
        templates.append('scenic view')
        templates.append('detailed background')
        templates.append('depth of field')
    if '厚涂' in style_desc or 'painterly' in style_lower or '史诗' in style_desc:
        templates.append('painterly style')
        templates.append('epic composition')
        templates.append('dramatic lighting')
    if '半写实' in style_desc or 'semi-realistic' in style_lower:
        templates.append('semi-realistic')
        templates.append('detailed face')
        templates.append('masterpiece quality')
    if '金属' in style_desc or 'metallic' in style_lower:
        templates.append('metallic texture')
        templates.append('reflective surface')
    if '暗黑' in style_desc or 'dark' in style_lower or '忧郁' in style_desc:
        templates.append('dark atmosphere')
        templates.append('dramatic shadows')
        templates.append('dark theme')
        templates.append('gothic aesthetic')
    if '科幻' in style_desc or 'sci-fi' in style_lower or '赛博' in style_desc:
        templates.append('mechanical parts')
        templates.append('industrial design')
    if '机械' in style_desc or 'mechanical' in style_lower:
        templates.append('mechanical parts')
        templates.append('robot')
    if '高饱和' in style_desc or 'vivid' in style_lower or '鲜艳' in style_desc:
        templates.append('vivid colors')
        templates.append('high saturation')
        templates.append('bold palette')
    if '潮流' in style_desc or '设计感' in style_desc or 'fashionable' in style_lower:
        templates.append('fashionable outfit')
        templates.append('trendy aesthetic')
    if '复古' in style_desc or 'retro' in style_lower or '90年代' in style_desc:
        templates.append('retro style')
        templates.append('grainy texture')
        templates.append('vintage colors')
        templates.append('90s anime style')
    if '美漫' in style_desc or 'comic' in style_lower:
        templates.append('comic style')
        templates.append('bold lines')
        templates.append('halftone')
        templates.append('rich textures')
    if '游戏' in style_desc or '概念' in style_desc or 'concept' in style_lower:
        templates.append('concept art')
        templates.append('dynamic pose')
        templates.append('detailed armor')
    if '透明' in style_desc or 'jelly' in style_lower or '果冻' in style_desc:
        templates.append('translucent colors')
        templates.append('soft gradient')
        templates.append('ethereal')
    if '动感' in style_desc or 'dynamic' in style_lower:
        templates.append('dynamic pose')
    if '霓虹' in style_desc or 'neon' in style_lower:
        templates.append('neon lights')
        templates.append('vibrant colors')
    if '水彩' in style_desc or 'watercolor' in style_lower:
        templates.append('watercolor effect')
    
    if not templates:
        templates.append('simple background')
        templates.append('gentle expression')
    
    seen = set()
    unique = []
    for t in templates:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    
    return f"@{tag}, 1girl, {{character}}, {', '.join(unique)}"

def main():
    out_dir, version = get_output_dir()
    print(f'\n=== 3_画师去重.py ===')
    print(f'输出目录: {out_dir} (v{version})\n')
    
    animadex_artists = parse_animadex_artists()
    csv_artists = parse_artists_csv()
    curated = parse_curated()
    
    merged = {}
    for tag, info in animadex_artists.items():
        merged[tag] = info
    for tag, info in csv_artists.items():
        if tag not in merged or info.get('works', 0) > merged[tag].get('works', 0):
            merged[tag] = info
    
    curated_tags = set(curated.keys())
    regular_lines = []
    curated_lines = []
    
    for tag in sorted(merged.keys()):
        if tag in curated_tags:
            continue
        info = merged[tag]
        name = info.get('name', '')
        if not name:
            name = tag
        works = info.get('works', 0)
        regular_lines.append(f'[DOMAIN:画师] [CAT:-] @{tag} | name: {name} | works: {works}')
    
    for tag in sorted(curated.keys()):
        info = curated[tag]
        name = info.get('name', '')
        style = info.get('style', '')
        cat = info.get('category', '')
        template = generate_artist_template(tag, style)
        curated_lines.append(f'[DOMAIN:画师精选] [CAT:{cat}] @{tag}')
        if name:
            curated_lines.append(f'  name: {name}')
        if style:
            curated_lines.append(f'  style: {style}')
        curated_lines.append(f'  template: {template}')
        curated_lines.append('---')
    
    if curated_lines and curated_lines[-1] == '---':
        curated_lines.pop()
    
    write_file(os.path.join(out_dir, 'artists_merged.txt'), regular_lines)
    write_file(os.path.join(out_dir, 'artists_curated.txt'), curated_lines)
    print(f'\n输出: artists_merged.txt ({len(regular_lines)} 行)')
    print(f'输出: artists_curated.txt ({len(curated_lines)} 行)')

if __name__ == '__main__':
    main()
