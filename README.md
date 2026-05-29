# Anima RAG 知识库

为 [ComfyUI Easy-RAG](https://github.com/nregret/Comfyui-Easy-RAG) 构建的 AI 绘画提示词知识库，专为 Anima 模型优化。

> 如何使用 EasyRAG 节点请参阅 [EasyRAG 官方文档](https://github.com/nregret/Comfyui-Easy-RAG)。

---

## 知识库内容（22 个文件）

| 类别 | 文件 | 数量 |
|---|---|---|
| 标签（全集） | `tags_all.txt` | 58,272 条 |
| 标签（按大类） | `tags_人物.txt` ~ `tags_无法分类.txt` | 11 个分类文件 |
| 角色 | `characters_merged.txt` | 34,301 个角色 |
| 画师 | `artists_merged.txt` | 20,605 个画师 |
| 精选画师+模板 | `artists_curated.txt` | 57 个精选画师 |
| 提示词示例 | `prompt_examples.txt` | 11,071 条 |
| 插画模板 | `templates_basic.txt` `templates_story.txt` | 插画基础、剧情主视觉 |
| 漫画模板 | `templates_comic.txt` | 漫画单页 |
| 视频模板 | `templates_keyframe.txt` | 首尾帧 |
| 修改模板 | `templates_inpaint.txt` | 局部重绘 |
| 增强规则 | `enhancement_rules.txt` | 10 条 V2 增强规则 |

所有文件均带 `[DOMAIN:xxx] [CAT:xxx]` 前缀标记，EasyRAG 检索时自动按领域分流。

`system_prompt.txt` 为 LLM 节点的 System Prompt 模板，使用时粘贴到节点输入框即可。

---

## 📋 模板触发指南

每个模板文件内置了 `[KEYWORDS: ...]` 标签。当你的 query 包含这些关键词时，EasyRAG 会自动匹配对应模板，LLM 按模板结构填空。即使 EasyRAG 未返回模板 chunk，System Prompt 中的强制路由规则也会根据你的关键词选择正确模板。

| 模板 | 触发关键词 | 你的槽位 |
|---|---|---|
| **插画基础** | `插画` `立绘` `角色图` `人物图` `单张` `basic` `illustration` | `{safety}` `{artist}` `{count}` `{character}` `{clothing}` `{pose}` `{scene}` `{lighting}` |
| **剧情主视觉** | `剧情封面` `海报` `主视觉` `电影海报` `key visual` `poster` `cinematic` | 基础槽位 + `{identity}` `{action}` `{conflict}` `{mood}` |
| **漫画单页** | `漫画` `黑白漫画` `日漫` `单页漫画` `manga` `comic` `monochrome` | `{safety}` `{artist}` `{count}` `{character}` `{action}` |
| **首尾帧** | `首尾帧` `动作过程` `从 到 变化` `图生视频` `关键帧` `keyframe` `image-to-video` | 基础槽位 + `{frame_type}` `{composition}` `{direction}` `{motion_hint}` |
| **局部重绘** | `局部重绘` `修改` `换发型` `换衣服` `inpaint` `retouch` | `{safety}` `{artist}` `{count}` `{character}` `{change_target}` |

### 触发示例

**插画基础**：`"帮我画一个穿 JK 制服的少女，anmi 风格"` → 命中 `插画 角色图` → LLM 填 `{clothing}=school uniform, {artist}=@anmi`

**剧情主视觉**：`"剧情封面，魔法少女对抗巨龙，wlop 风格"` → 命中 `剧情封面 poster` → LLM 填 `{identity}=magical girl, {action}=casting a spell, {conflict}=dark dragon`

**漫画单页**：`"黑白日漫风格，初音在雨中奔跑"` → 命中 `漫画 monochrome manga` → LLM 填 `{character}=hatsune miku, {action}=running through rain`

**首尾帧**：`"图生视频，战斗拔刀过程，女剑士从收刀到斩击完成"` → 命中 `动作过程 从 到 变化 keyframe` → LLM 输出两帧，用 `---` 分隔

**局部重绘**：`"给初音换个短发，其余不变"` → 命中 `修改 换发型 inpaint` → LLM 填 `{change_target}=short bob cut`

**增强规则**：`"画面太平淡了，加点冲击力"` → 命中 `平淡 视觉冲击` → LLM 追加 `dramatic lighting, depth of field, cinematic composition`

### 格式注意事项

- 标签层和自然语言层之间**必须有一个空行**
- 禁止 NL 句式混入标签区 — `with long hair` → `long hair`
- 同义标签不堆叠 — `blowjob, fellatio` → 只保留一个
- `{safety}` 由 LLM 自动判断（`safe` / `sensitive` / `nsfw` / `explicit`），无需用户手动选择
- 权重语法：Anima 支持 `(tag:1.5)` 格式，但画师标签响应阈值较高（建议 ≥1.5）。每个权重标签多占 5~6 token，堆叠过多会耗尽 512 token 窗口

---

## 从原始数据构建

```bash
cd scripts
python 1_tag_生成.py; python 2_角色合并.py; python 3_画师去重.py
python 4_prompt_prep.py; python 5_模板生成.py
```

---

## 数据来源

`知识库/` 中的所有文件为数据处理后的整理产物。原始数据来自以下公开项目：

| 原始数据 | 来源 | 用途 |
|---|---|---|
| Danbooru e261 标签集 | QQ群友天痕（翻译+分类） | 标签主库 |
| Anima 标签白名单 | [BetaDoggo/danbooru-tag-list](https://github.com/BetaDoggo/danbooru-tag-list/releases) (`anima-1.0.csv`) | 标签过滤 |
| 角色/画师索引 | [fulletLab/comfyui-anima-style-nodes](https://github.com/fulletLab/comfyui-anima-style-nodes) → [Laxhar/noob-wiki](https://huggingface.co/datasets/Laxhar/noob-wiki) | 角色库、画师库 |
| 画师精选、提示词示例 | [nregret/Comfyui-Easy-RAG](https://github.com/nregret/Comfyui-Easy-RAG) (`rag/`) | 精选画师、提示词参考 |
| 角色验证数据 | [hbl917070/DrawingSpells](https://github.com/hbl917070/DrawingSpells) → [NebulaeWis/e621-2024](https://huggingface.co/datasets/NebulaeWis/e621-2024-webp-4Mpixel) | 角色中文名匹配 |

### 模板与规则设计参考

| 参考资料 | 性质 | 来源 |
|---|---|---|
| `Anima_提示词规则.txt` | Anima 提示词格式说明 | [nnegret_哥们老实人](https://space.bilibili.com/35773509)（EasyRAG 作者） |
| `anima规则(概念神版).txt` | 概念神增强策略 | QQ群友 三费武装白色人种 |
| `Anima_提示词规则_AI-KSK(2).docx` | Anima 实战指南 | [AI-KSK](https://space.bilibili.com/110353151) |

以上均为无偿分享。原始数据版权归各自来源所有。本仓库仅做格式整理与分类优化，不施加额外限制。

---

## 使用工具

| 工具 | 用途 |
|---|---|
| Python（标准库） | 数据处理脚本 |
| DeepSeek V4 Pro | 代码审查、分类逻辑设计、模板设计 |
| ComfyUI Easy-RAG | 部署平台 |

## 说明

本项目由单人 + AI 辅助，精力有限，可能存在疏漏，敬请谅解。欢迎提交 Issues。

## 许可

- 处理脚本（`scripts/`）：**MIT License**
- 知识库文件（`知识库/`）：整理自公开数据源，**永久免费开放**

> ⚠️ 如果你在付费渠道获得此知识库，你被骗了。本仓库始终免费提供最新版本。遇到倒卖请到 [C 站私信我](https://civitai.red/user/BuXinZi) 告知。

## 作者

**炼天魔尊分魂-不信子 (BuXinZi)** — GitHub · Civitai（发布 LoRA 模型，欢迎关注）| 未开设任何 QQ 群/微信群/付费频道。

## 相关项目

ComfyUI Easy-RAG · Anima Style Explorer · AnimaDex · BetaDoggo/danbooru-tag-list · DrawingSpells · Laxhar/noob-wiki · NebulaeWis/e621-2024
