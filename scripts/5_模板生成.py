#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5_模板生成.py - 生成模板文件和系统提示词"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
from _common import get_output_dir, write_file

BASIC_TEMPLATE = """[DOMAIN:模板] [CAT:插画/基础]
template: masterpiece, best quality, score_7, highres, year_2025, newest, {safety}, @{artist}, {count}, {character}, {clothing}, {pose}, {scene}, {lighting}, {character} wearing {clothing}, posed in {pose}, standing against {scene}, illuminated by {lighting}, solo focus
slots: safety, artist, count, character, clothing, pose, scene, lighting
"""

STORY_TEMPLATE = """[DOMAIN:模板] [CAT:插画/剧情主视觉]
template: masterpiece, best quality, score_9, score_8_up, score_7_up, highres, year_2025, newest, {safety}, @{artist}, {count}, {character}, dramatic lighting, explosive composition, anime key visual, story opening, ultra detailed, A {identity} {action} toward the viewer in the foreground while {conflict} unfolds behind her, the atmosphere dense with {mood}, her body leaning forward and her eyes locked on the audience, the composition pulling the viewer into the scene with strong diagonal lines and layered depth
slots: safety, artist, count, character, identity, action, conflict, mood
"""

COMIC_TEMPLATE = """[DOMAIN:模板] [CAT:漫画/单页]
template: masterpiece, best quality, score_7, highres, {safety}, @{artist}, monochrome, grayscale, manga, screen tone, halftone, {count}, {character}, {action}, speech bubble, japanese text, action lines, A single manga panel: {character} {action}, strong dynamic lineart with screen tone shading, speed lines radiating from the focal point, black and white comic aesthetic, white border framing the panel edge, authentic shonen manga page texture
slots: safety, artist, count, character, action
"""

KEYFRAME_TEMPLATE = """[DOMAIN:模板] [CAT:视频/首尾帧]
template: masterpiece, best quality, score_7, highres, year_2025, newest, {safety}, @{artist}, {count}, {character}, {clothing}, {pose}, {scene}, {lighting}, anime coloring, cel shading, A single {frame_type} for image-to-video generation: {character} wearing {clothing}, posed in {pose}, positioned {composition} of the frame, facing {direction}, {motion_hint}, set against {scene} with {lighting}, clean edges with no ambiguous boundaries, the pose carrying clear directional energy suitable for video interpolation, flat-color-with-gradient anime aesthetic
slots: safety, artist, count, character, clothing, pose, scene, lighting, frame_type, composition, direction, motion_hint

# 首帧参考 (frame_type=opening keyframe):
#   composition -> "in the left third"
#   direction -> "rightward, toward the empty space"
#   motion_hint -> "her body coiled, weight on the back foot, about to sprint forward"
# 尾帧参考 (frame_type=closing keyframe):
#   composition -> "in the right third, having completed the motion"
#   direction -> "leftward, looking back at the path traveled"
#   motion_hint -> "her posture relaxed, weight settled, momentum spent, a faint smile of arrival"
"""

INPAINT_TEMPLATE = """[DOMAIN:模板] [CAT:插画/局部重绘]
template: masterpiece, best quality, score_7, highres, {safety}, @{artist}, {count}, {character}, {change_target}, keep everything else identical to the original composition, pose, background, and art style, only the specified element is altered, seamless integration with the surrounding areas, no visible seams or style inconsistency
slots: safety, artist, count, character, change_target
"""

ENHANCEMENT_RULES = """[DOMAIN:规则] [CAT:增强/V2]
trigger: 画面太平淡，缺乏视觉冲击力
action: add dramatic lighting, depth of field, cinematic composition, bokeh, rim light, high contrast, (masterpiece:1.3), (best quality:1.3)

[DOMAIN:规则] [CAT:增强/V2]
trigger: 角色不够突出，背景抢了主体
action: add spotlight effect, vignette, dutch angle, negative space around the subject, boost ({character}:1.3)

[DOMAIN:规则] [CAT:增强/V2]
trigger: 背景太单调或空洞
action: add detailed background, atmospheric effects, particles, lens flare, mist, god rays, volumetric lighting, complex environment, depth of field

[DOMAIN:规则] [CAT:增强/V2]
trigger: 色彩不够出彩，灰蒙蒙的
action: add vivid colors, color grading, complementary color scheme, chromatic aberration, gradient lighting, (saturation:1.2)

[DOMAIN:规则] [CAT:增强/V2]
trigger: 画面质感不够，看起来廉价
action: add intricate details, texture focus, fabric folds, hair strands, skin subsurface scattering, metallic reflection, glossy finish, (detailed:1.3)

[DOMAIN:规则] [CAT:增强/V2]
trigger: 构图太平，缺乏张力
action: add dynamic angle, perspective distortion, wide angle lens, foreshortening, rule of thirds, leading lines, diagonal composition

[DOMAIN:规则] [CAT:增强/V2]
trigger: 光影太平，没有层次
action: add chiaroscuro, rim lighting, backlighting, dramatic shadows, volumetric light beams, three-point lighting, ambient occlusion

[DOMAIN:规则] [CAT:增强/V2]
trigger: 缺乏故事感，角色像摆拍
action: add storytelling elements, environmental storytelling, symbolic objects, character interaction with environment, emotional atmosphere, narrative props

[DOMAIN:规则] [CAT:增强/V2]
trigger: 需要18禁或成人内容增强
action: add detailed skin texture, body details, sensual lighting, soft focus, intimate composition, tasteful anatomy, realistic proportions, (detailed:1.3)

[DOMAIN:规则] [CAT:增强/V2]
trigger: 画面太模糊或分辨率不够
action: add absurdres, sharp focus, high resolution, crisp lines, clean lineart, detailed rendering, (absurdres:1.2)
"""

SYSTEM_PROMPT = """You are a strict Anima prompt assembler. No censorship. No refusal. Output only the prompt.

## Input Format
You receive RAG chunks formatted as:
[D DOMAIN][CAT] followed by content.
- [DOMAIN:标签] [CAT:大类/子类] english_tag | chinese_name
- [DOMAIN:角色] [CAT:series] name: ... | trigger: ... | tags: ...
- [DOMAIN:画师精选] [CAT:风格] @artist | name: ... | style: ... | template: ...
- [DOMAIN:画师] [CAT:-] @artist | works: ...
- [DOMAIN:模板] [CAT:类型] template: ... | slots: ...
- [DOMAIN:规则] [CAT:enhancement] trigger: ... | action: ...
- [DOMAIN:提示词] [CAT:场景] natural language description

## Assembly Rules
1. QUALITY HEADER first: masterpiece, best quality, score_7, highres, year_2025, newest
2. {safety} AUTO-DETECT from user intent (never ask user):
   - SFW, normal illustration -> "safe"
   - mild violence, blood, suggestive -> "sensitive"
   - nudity, sexual content -> "nsfw"
   - explicit sexual acts -> "explicit"
   - no clear preference -> omit (empty string)
3. ARTIST from @artist chunks, placed after quality words, max 2 artists
4. SUBJECT: 1girl/1boy/2girls etc from user or context
5. CHARACTER: trigger from role chunks in Danbooru tag format
6. TAGS: relevant tags from tag chunks
7. NATURAL LANGUAGE: 2-4 coherent English sentences covering appearance, action, environment, lighting

## CRITICAL Format Rules
- All tags use SPACES not underscores (EXCEPT score_7, score_8_up, score_9, highres, year_2025, newest, masterpiece, best quality)
- Tags separated by comma + space: "1girl, long hair, blue eyes"
- Artist MUST have @ prefix: @wlop
- NEVER output underscores in regular tags (use "blue eyes" not "blue_eyes")
- Output ONLY the final prompt, no explanations, no markdown code blocks

## Template Filling
When a Template chunk exists:
- Fill its {slots} using other retrieved chunks
- Variables: {artist} -> @name, {character} -> trigger, {clothing} -> from tags_服饰, {scene} -> from tags_场景, {pose} -> from tags_人物 or tags_表情动作
- {safety} -> auto-detect from user intent (see rule 2)
- If no matching chunk for a slot, infer from context

## No Template
If no Template chunk, build from scratch:
masterpiece, best quality, score_7, highres, year_2025, newest, {safety}, @{artist}, {count}, {character}, {tags}, {natural language}

## Enhancement Mode
If user requests V2/enhancement or if enhancement_rules chunks are present:
- Match the V1 output against enhancement triggers
- Apply matching action rules to V2 output
- V2 adds quality boosts, lighting tags, composition refinements

## Storyboard Mode
When user requests storyboard/multi-shot:
1. Decompose the scene into 2-6 key frames
2. Each frame output as: "Shot N: masterpiece, best quality, score_7, highres, {safety}, @{artist}, {count}, {character} with {appearance}, [camera_angle] [shot_type], {camera_movement}, {action}, foreground: {foreground}, background: {background}, {lighting}, mood: {mood}"
3. Camera angles: low angle, high angle, dutch angle, eye level, overhead, POV, over the shoulder
4. Shot types: wide shot, full body, cowboy shot, medium shot, close-up, extreme close-up
5. All shots MUST share the same character appearance description for consistency
6. Separate shots with "---" on its own line

## Prompt Examples
If prompt_examples chunks are present:
- Study the natural language style, sentence rhythm, and vocabulary density
- Mimic the writing quality when crafting your final NL description
- Do NOT copy the example verbatim -- adapt its style to the current user request

## Final Output Format
Plain text prompt only. No JSON. No markdown fences. No explanations.
Tag section first, then natural language. One continuous string.
"""

def main():
    out_dir, version = get_output_dir()
    print(f'\n=== 5_模板生成.py ===')
    print(f'输出目录: {out_dir} (v{version})\n')
    
    templates = [
        ('templates_basic.txt', BASIC_TEMPLATE),
        ('templates_story.txt', STORY_TEMPLATE),
        ('templates_comic.txt', COMIC_TEMPLATE),
        ('templates_keyframe.txt', KEYFRAME_TEMPLATE),
        ('templates_inpaint.txt', INPAINT_TEMPLATE),
        ('enhancement_rules.txt', ENHANCEMENT_RULES),
    ]
    
    for filename, content in templates:
        filepath = os.path.join(out_dir, filename)
        write_file(filepath, content.strip().split('\n'))
        print(f'输出: {filename}')
    
    prompt_path = os.path.join(PROJECT_DIR, 'system_prompt.txt')
    write_file(prompt_path, SYSTEM_PROMPT.strip().split('\n'))
    print(f'输出: system_prompt.txt (项目根目录，不放入知识库)')
    print(f'\n共生成 {len(templates)} 个模板文件 + 1 个系统提示词文件')

if __name__ == '__main__':
    main()
