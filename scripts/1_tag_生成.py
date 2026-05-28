#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1_tag_生成.py - 标签白名单过滤 + 分类优化"""

import csv
import os
import sys
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
from _common import get_output_dir, write_file, progress_bar

SOURCE_DIR = os.path.join(PROJECT_DIR, 'source')
E261_CSV = os.path.join(SOURCE_DIR, 'danbooru_e261_updated.csv')
ANIMA_CSV = os.path.join(SOURCE_DIR, 'anima-1.0 (1).csv')

def load_anima_whitelist():
    tags = set()
    aliases = set()
    with open(ANIMA_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                tag = row[0].strip()
                if tag:
                    tags.add(tag)
                if len(row) >= 4 and row[3]:
                    for alias in row[3].split(','):
                        a = alias.strip()
                        if a:
                            aliases.add(a)
    whitelist = tags | aliases
    print(f'[INFO] Anima 白名单: {len(tags)} tags + {len(aliases)} aliases = {len(whitelist)} 唯一标签')
    return whitelist, tags

def load_e261_char_info():
    """从 e261 二次元角色中提取系列前缀和角色前缀用于分类"""
    series_set = set()
    char_prefix = set()
    with open(E261_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 4:
                continue
            eng, chn, cat = row[0], row[1], row[2]
            if cat != '二次元角色':
                continue
            if '_(' in eng:
                parts = eng.split('_(')
                series_set.add(parts[-1].rstrip(')'))
            else:
                char_prefix.add(eng)
                if '_(series)' not in eng and '_(anime)' not in eng and '_(species)' not in eng:
                    series_set.add(eng)
    return series_set, char_prefix

KNOWN_WORKS = {
    'arknights', 'genshin_impact', 'touhou', 'fate', 'pokemon', 'vocaloid',
    'blue_archive', 'hololive', 'kantai_collection', 'love_live',
    'azur_lane', 'honkai', 'bang_dream', 'idolmaster', 'girls_frontline',
    'granblue_fantasy', 'project_sekai', 'uma_musume', 'nier', 're:zero',
    'reverse:1999', 'zenless_zone_zero', 'wuthering_waves', 'star_rail',
    'street_fighter', 'king_of_fighters', 'guilty_gear', 'tekken',
    'final_fantasy', 'dragon_quest', 'monster_hunter', 'persona', 'zelda',
    'fire_emblem', 'xenoblade', 'splatoon', 'animal_crossing', 'kirby',
    'super_mario', 'sonic_the_hedgehog', 'metal_gear', 'resident_evil',
    'devil_may_cry', 'castlevania', 'ace_attorney', 'tales_of',
    'league_of_legends', 'overwatch', 'world_of_warcraft', 'minecraft',
    'warhammer', 'dungeons_and_dragons', 'dungeon_meshi', 'spy_x_family',
    'one_punch_man', 'bocchi_the_rock', 'chainsaw_man', 'oshi_no_ko',
    'jujutsu_kaisen', 'demon_slayer', 'frieren', 'delicious_in_dungeon',
    'tatami_galaxy', 'monogatari', 'steins;gate', 'madoka_magica',
    'evangelion', 'haruhi_suzumiya', 'k-on', 'lucky_star', 'nichijou',
    'toradora', 'angel_beats', 'clannad', 'kanon', 'air',
    'sword_art_online', 'attack_on_titan', 'fullmetal_alchemist',
    'cowboy_bebop', 'samurai_champloo', 'trigun', 'gurren_lagann',
    'kill_la_kill', 'panty_and_stocking', 'flcl', 'space_dandy',
    'madoka', 'violet_evergarden', 'a_silent_voice', 'your_name',
    'weathering_with_you', 'suzume', 'spirited_away', 'howl',
    'princess_mononoke', 'my_neighbor_totoro', 'ponyo',
    'to_heart', 'comic_party', 'utawarerumono', 'white_album',
    'nisekoi', 'bakemonogatari', 'nisemonogatari', 'kizumonogatari',
    'soul_worker', 'warship_girls', 'south_park', 'diamond_wa_kudakenai',
    'how_to_train_your_dragon', 'avatar_the_last_airbender',
    'cardfight_vanguard', 'skyrim', 'dota', 'plants_vs_zombies',
    'plants_vs._zombies', 'grand_theft_auto', 'magi', 'marvel',
    'baldur', 'dungeons_&_dragons', 'how_to', 'puzzle_&_dragons',
    'world_of_tanks', 'world_of_warships', 'call_of_duty',
    'dead_or_alive', 'soul_calibur', 'blazblue', 'melty_blood',
    'under_night', 'dragon_ball', 'naruto', 'bleach', 'one_piece',
    'jojo', 'hunter_x_hunter', 'yu_yu_hakusho', 'gintama',
    'fairy_tail', 'black_clover', 'my_hero_academia', 'haikyuu',
    'kuroko', 'slam_dunk', 'initial_d', 'wangan_midnight',
    'transformers', 'gundam', 'macross', 'code_geass', 'geass',
}

META_KW = {
    'character_name', 'artist_name', 'copyright_name', 'character_request',
    'copyright_request', 'translation_request', 'source_request',
    'weapon_request', 'parody_request', 'gender_request', 'check_character',
    'check_copyright', 'check_artist', 'check_translation', 'check_commentary',
    'hashtag-only_commentary', 'commentary_typo', 'partial_commentary',
    'character_charm', 'pokemon_(species)', 'digimon_(species)',
    'generation_1_pokemon', 'borrowed_character', 'profile', 'url',
    'translated', 'hard-translated', 'hard_translated', 'bad_link',
    'md5_mismatch', 'resolution_mismatch', 'webm', 'web_address',
    'twitter_username', 'pixiv_username', 'pixiv_id', 'deviantart_username',
    'instagram_username', 'fanbox_username', 'fanbox_reward', 'patreon_username',
    'subscribestar_username', 'furaffinity_username', 'tumblr_username',
    'bilibili_username', 'lofter_username', 'bcy_username', 'artstation_username',
    'weibo_username', 'youtube_username', 'facebook_username', 'hentai-foundry_username',
    'gumroad_username', 'bluesky_username', 'commissioner_name', 'creator_name',
    'song_name', 'group_name', 'company_name', 'circle_name', 'vehicle_name',
    'album_name', 'copyright_notice', 'copyright_name', 'content_rating',
    'song_name', 'name_connection', 'number', 'numbered', 'tagme',
    'symbol', 'pun', 'net',
}

def classify_char_tag(eng, series_set, char_prefix):
    """对二次元角色标签进行分类: role / series / meta"""
    if eng in META_KW:
        return '元数据'
    if '_(' in eng:
        if eng in KNOWN_WORKS:
            return '作品'
        parts = eng.split('_(')
        series = parts[-1].rstrip(')')
        if series in series_set or series in KNOWN_WORKS:
            return '角色'
        return '角色'
    if eng in series_set or eng in KNOWN_WORKS:
        return '作品'
    if eng in char_prefix and eng not in KNOWN_WORKS:
        return '角色'
    prefix = eng[:3]
    if prefix and prefix in series_set:
        for s in series_set:
            if eng.endswith('_' + s) or f'_{s}_' in eng or eng == s:
                return '作品'
    return '作品'

def recategorize_unknown(tag_lines, series_set, char_prefix):
    new_lines = []
    moved_action = 0
    moved_char_series = 0
    moved_char_role = 0
    
    for line in tag_lines:
        if not line.startswith('[DOMAIN:标签] [CAT:无法分类]'):
            new_lines.append(line)
            continue
        
        match = re.match(r'\[DOMAIN:标签\] \[CAT:无法分类\] (.+?)\|', line)
        if not match:
            new_lines.append(line)
            continue
        eng = match.group(1).strip()
        
        # 1. 含 _(): 角色名
        if '_(' in eng:
            new_lines.append(line.replace('无法分类', '二次元角色/角色'))
            moved_char_role += 1
            continue
        
        # 2. 含 `:` 冒号: 作品
        if ':' in eng and '_' in eng:
            new_lines.append(line.replace('无法分类', '二次元角色/作品'))
            moved_char_series += 1
            continue
        
        # 3. 简单系列名或已知作品
        if eng in series_set or eng in KNOWN_WORKS or eng in META_KW:
            if eng in META_KW:
                new_lines.append(line.replace('无法分类', '二次元角色/元数据'))
            else:
                new_lines.append(line.replace('无法分类', '二次元角色/作品'))
                moved_char_series += 1
            continue
        
        # 4. 长于 6 且含 _ 不像动作标签
        if len(eng) > 6 and '_' in eng:
            prefix = eng[:3]
            if prefix and prefix in char_prefix:
                new_lines.append(line.replace('无法分类', '二次元角色/角色'))
                moved_char_role += 1
                continue
        
        new_lines.append(line)
    
    print(f'[重分类] 无法分类 → 表情动作: {moved_action}')
    print(f'[重分类] 无法分类 → 二次元角色/作品: {moved_char_series}')
    print(f'[重分类] 无法分类 → 二次元角色/角色: {moved_char_role}')
    return new_lines

def process_e261(whitelist, anima_tags, series_set, char_prefix):
    cat_groups = {}
    total = 0
    filtered = 0
    
    with open(E261_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            total += 1
            if len(row) < 4:
                continue
            eng, chn, cat, subcat = row[0], row[1], row[2], row[3] if len(row) > 3 else ''
            eng = eng.strip()
            chn = chn.strip()
            cat = cat.strip()
            subcat = subcat.strip()
            
            if eng not in whitelist:
                continue
            filtered += 1
            
            if cat == '二次元角色' and '/' not in cat:
                sub_class = classify_char_tag(eng, series_set, char_prefix)
                subcat = sub_class
            
            cat_display = cat
            if subcat:
                cat_display = f'{cat}/{subcat}'
            
            line = f'[DOMAIN:标签] [CAT:{cat_display}] {eng} | {chn}'
            if cat not in cat_groups:
                cat_groups[cat] = []
            cat_groups[cat].append(line)
    
    print(f'\n[统计] e261 总计: {total}')
    print(f'[统计] 通过 anima 白名单: {filtered} ({filtered/total*100:.1f}%)')
    return cat_groups

def main():
    out_dir, version = get_output_dir()
    print(f'\n=== 1_tag_生成.py ===')
    print(f'输出目录: {out_dir} (v{version})\n')
    
    whitelist, anima_tags = load_anima_whitelist()
    series_set, char_prefix = load_e261_char_info()
    print(f'[INFO] 二次元角色系列前缀: {len(series_set)}, 角色前缀: {len(char_prefix)}')
    
    cat_groups = process_e261(whitelist, anima_tags, series_set, char_prefix)
    
    # 收集所有行
    all_lines = []
    for cat in sorted(cat_groups.keys()):
        all_lines.extend(cat_groups[cat])
    
    # 重新分类无法分类
    all_lines = recategorize_unknown(all_lines, series_set, char_prefix)
    
    # 重建 cat_groups
    new_cat_groups = {}
    for line in all_lines:
        m = re.match(r'\[DOMAIN:标签\] \[CAT:(.+?)\]', line)
        if m:
            cat = m.group(1).split('/')[0]
            if cat not in new_cat_groups:
                new_cat_groups[cat] = []
            new_cat_groups[cat].append(line)
    
    print(f'\n--- 最终分类分布 ---')
    total_output = 0
    for cat in sorted(new_cat_groups.keys()):
        lines = new_cat_groups[cat]
        total_output += len(lines)
        print(f'  {cat}: {len(lines)} 条')
    print(f'  总计: {total_output} 条')
    
    # 写入文件
    tag_dir = os.path.join(out_dir, 'tags')
    os.makedirs(tag_dir, exist_ok=True)
    
    all_lines_final = []
    for cat in sorted(new_cat_groups.keys()):
        lines = new_cat_groups[cat]
        all_lines_final.extend(lines)
        safe_cat = cat.replace('/', '_')
        write_file(os.path.join(out_dir, f'tags_{safe_cat}.txt'), lines)
    
    write_file(os.path.join(out_dir, 'tags_all.txt'), all_lines_final)
    print(f'\n输出: tags_all.txt ({len(all_lines_final)} 行)')
    print(f'输出: {len(new_cat_groups)} 个分类文件')

if __name__ == '__main__':
    main()
