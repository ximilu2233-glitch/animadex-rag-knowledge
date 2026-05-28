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

## 从原始数据构建

如果你想从原始数据重新构建知识库：

```bash
# 1. 将以下源文件放入 source/ 目录（通过下方链接获取）
#    danbooru_e261_updated.csv
#    anima-1.0 (1).csv
#    animadex_index.csv
#    artists.csv
#    画师精选.csv → 重命名为 画师精选.md
#    1万条提示词完整版.csv

# 2. 运行构建脚本
cd scripts
python 1_tag_生成.py
python 2_角色合并.py
python 3_画师去重.py
python 4_prompt_prep.py
python 5_模板生成.py
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

以上均为无偿分享。

以上原始数据版权归各自来源所有。本仓库仅做格式整理与分类优化，不施加额外限制。

---

## 使用工具

| 工具 | 用途 |
|---|---|
| Python（标准库） | 5 个数据处理脚本 + 共享模块 |
| DeepSeek V4 Pro | 代码审查、分类逻辑设计、模板设计辅助 |
| ComfyUI Easy-RAG | 目标部署平台（RAG 检索） |

---

## 说明

本项目由单人 + AI 辅助完成，精力有限，可能存在疏漏或分类不准确之处，还请谅解。如有问题欢迎提交 [Issues](../../issues)。

---

## 许可

- 处理脚本（`scripts/`）：**MIT License**
- 知识库文件（`知识库/`）：整理自上述公开数据源，**永久免费开放**

> ⚠️ 如果你在淘宝/闲鱼/付费群等渠道付费获得了此知识库，你被骗了。  
> 本仓库始终免费提供最新版本。遇到倒卖请帮忙举报，也可以到 [C 站私信我](https://civitai.red/user/BuXinZi) 告知。

---

## 作者

**炼天魔尊分魂-不信子 (BuXinZi)**

- GitHub：[github.com/BuXinZi](https://github.com/BuXinZi)
- Civitai：[civitai.red/user/BuXinZi](https://civitai.red/user/BuXinZi)（偶尔发布 LoRA 模型，欢迎关注）
- B 站教程、教学视频等可直接使用，注明出处即可

> ⚠️ 本人未开设任何 QQ 群/微信群/付费频道。如遇到以"不信子"名义建立的群组均为假冒，请警惕。  
> 偶尔能在一些 AI 绘画交流群见到我（虽然也就是个底边而已，笑）。

---

## 相关项目

- [ComfyUI Easy-RAG](https://github.com/nregret/Comfyui-Easy-RAG) — RAG 节点插件
- [Anima Style Explorer](https://github.com/fulletLab/comfyui-anima-style-nodes) — 画师/角色浏览器
- [AnimaDex](https://github.com/zetaneko/AnimaDex) — 角色/画师索引与自托管画廊（animadex.net 后端）
- [BetaDoggo/danbooru-tag-list](https://github.com/BetaDoggo/danbooru-tag-list) — 模型标签列表
- [DrawingSpells](https://github.com/hbl917070/DrawingSpells) — 角色提示词查询工具
- [Laxhar/noob-wiki](https://huggingface.co/datasets/Laxhar/noob-wiki) — Animadex 底层角色/画师数据集
- [NebulaeWis/e621-2024](https://huggingface.co/datasets/NebulaeWis/e621-2024-webp-4Mpixel) — DrawingSpells 底层图像数据集
