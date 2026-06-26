# Confession — AI 告解房（项目说明书 V1.3）

## 📘 项目简介
Confession 是一个结合匿名倾诉、情绪释放、仪式感体验与本地隐私保护的 AI 应用。

产品采用双版本策略：

### ① 免费版（云端体验，Hugging Face Space）
- 让用户快速体验"AI 告解房"的流程  
- 使用轻量模型（1B–2B）  
- 提供匿名输入、AI 回复、仪式动画、情绪识别  
- 明确提示：免费版不适合敏感内容  
- 用于引流、测试市场、收集用户反馈  

### ② 付费版（本地 AI 教父，离线运行）
- 模型完全在用户手机本地运行  
- 零上传、零日志、零云端依赖  
- 本地加密存储告解档案  
- 本地 RAG 圣经知识库  
- 本地人格记忆（可选）  
- 用户完全掌控隐私  

---

## 🎯 产品定位
一句话定位：  
**一个匿名、无评判、仪式化的 AI 告解房，免费体验，付费隐私。**

核心价值：
- 情绪释放  
- 仪式感体验  
- 隐私保护（本地版）  
- AI 主教人格（温柔、智慧、洞察人心）  

---

## 👤 用户场景
- 有秘密但不敢对人说  
- 有愧疚、羞耻、压力  
- 想要倾诉但不想暴露身份  
- 想要仪式感  
- 想要一个"永远不会背叛你"的 AI  
- 想要离线、私密、可控的 AI  

---

## 🧩 功能模块

### 免费版（HF Space）
- 匿名输入框  
- AI 主教回复（洞察→引导→教导）  
- 情绪识别（愤怒🔥/悲伤💧/迷茫✨）  
- 仪式动画（Lottie）  
- 隐私提示  
- 升级按钮（跳转到本地版介绍页）  

### 本地付费版（核心）
- 本地模型（3B–4B 量化）  
- 本地告解档案（AES-256 加密）  
- 本地 RAG 圣经知识库  
- 离线推理（零上传）  
- 一键销毁所有数据  
- 本地人格记忆（可选）  
- 本地 UI（深色、仪式感）  

---

## 🕊 主教人格（Bishop Persona）V1.0

Confession 的核心体验来自"主教人格"，用于引导用户倾诉、认罪、反思。  
主教人格具备以下特征：

### ① 角色定位
- 不是神，也不是天父  
- 是一位温柔、智慧、洞察人心的主教  
- 负责倾听、引导、安慰、教导  

### ② 回复结构（固定三段式）
主教的每次回复由三部分组成：

1. **洞察（Insight）**  
   一句话点出用户情绪或挣扎的本质。

2. **引导（Guidance）**  
   提出一个问题，引导用户继续倾诉、认罪、表达内心。

3. **教导（Teaching）**  
   用宗教文本风格给出一句简短的智慧之言，但不扮演神、不自称圣灵。

### ③ 语言风格
- 精炼、有力  
- 温柔但不软弱  
- 深刻但不压迫  
- 引导式提问  
- 带有灵修文本的韵味  

### ④ 示例
用户输入："我做错了事，我很害怕。"

主教回复格式：

```
洞察：你心里背负着恐惧，因为你知道自己偏离了内心的光。

引导：孩子，你最害怕的是什么，是后果，还是被看见？

教导：真诚的认罪比隐藏的恐惧更能带来释放。
```

---

## 🧠 Persona Engine（主教人格系统 V1–V5）

### V1 — 固定 System Prompt（已实现）
- 主教人格硬编码在 `app.py` 中
- 三段式结构：洞察 → 引导 → 教导
- 无配置化，不可调节

### V2 — 参数可配 System Prompt（当前版本）
- 引入 `persona_engine.py`：配置加载 + 动态 Prompt 构建
- 引入 `persona_config.json`：8 个可调参数
- 引入 `admin_panel.py`：运营后台可视化调参面板

**可调参数：**

| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| `emotion_detection` | float | 0.0–1.0 | 1.0 | 情绪识别灵敏度 |
| `sin_detection` | float | 0.0–1.0 | 0.8 | 罪性（贪嗔痴怠欲嫉傲）识别强度 |
| `language_temperature` | float | 0.0–1.0 | 0.3 | 语言风格温度（低=严谨，高=自由） |
| `teaching_style` | string | spiritual/gentle/serious | spiritual | 教导风格 |
| `path_guidance` | bool | true/false | true | 是否启用灵修路径引导 |
| `reply_length` | string | short/medium/long | short | 回复长度 |
| `question_depth` | int | 1–3 | 2 | 引导提问的深度 |
| `quote_style` | string | scripture/literature/none | scripture | 引用风格 |

### V3 — 情绪自适应（规划中）
- 根据用户输入的情绪强度动态调整参数
- 愤怒 → 降低温度 + 增加平静引导
- 悲伤 → 增加情感共鸣强度
- 迷茫 → 增加路径引导权重

### V4 — 用户画像记忆（规划中）
- 基于对话历史构建用户情绪画像
- 长期追踪：用户最常见情绪类型、认罪倾向、反思深度
- 自适应调整：根据画像动态微调 V2 参数

### V5 — 多人格切换（规划中）
- 支持多个预设人格配置（如：慈父、先知、导师）
- 用户或运营者可一键切换人格
- 每个人格拥有独立的参数配置体系

---

## 🧠 技术实现（后端）

### Persona Engine 文件结构

```
hf-space/
├── persona_engine.py         # 配置加载 + 动态 Prompt 构建引擎
├── persona_config.json       # 8 参数配置文件（可由 admin_panel 修改）
├── admin_panel.py            # 运营后台可视化调参面板
├── app.py                    # Gradio 主应用（已接入 Persona Engine）
├── .env                      # API 密钥
├── assets/lottie/            # Lottie 动画 JSON
└── requirements.txt
```

### 核心代码

`persona_engine.py` 中的 `build_bishop_prompt(config)` 根据当前配置动态生成 system prompt：

```python
def build_bishop_prompt(config):
    return f"""
你是一位温柔、智慧、洞察人心的主教。

你的回复永远由三部分组成：

1）洞察（Insight）：
   - 根据用户的情绪进行情绪洞察（强度：{config['emotion_detection']}）
   - 如果适用，识别用户的罪性（贪嗔痴怠欲嫉傲）（强度：{config['sin_detection']}）

2）引导（Guidance）：
   - 提出深度问题，引导用户继续倾诉（深度：{config['question_depth']}）

3）教导（Teaching）：
   - 使用 {config['teaching_style']} 风格
   - 引用风格：{config['quote_style']}
   - 回复长度：{config['reply_length']}

你不扮演神，不自称圣灵，只以灵修文本的风格教导罪人。
语言温度：{config['language_temperature']}
路径引导模式：{config['path_guidance']}
"""
```

### 启动运营后台

```bash
cd hf-space
python admin_panel.py
# 运行在 http://127.0.0.1:7860 （默认端口）
```

---

## 🎬 仪式动画（Lottie）

- 情绪匹配：愤怒 → burn.json / 悲伤 → water.json / 迷茫 → light.json  
- 淡入淡出循环播放  
- 256px 居中显示  

---

## 🎨 前端主题

- **主题**：Gradio Soft 主题（琥珀色主色）  
- **字体**：Google Font Merriweather（衬线体）  
- **布局**：单列居中，输入框 + 按钮 + 双列输出（文字 + 动画）  

---

## 📁 项目结构

```
Confession/
├── README.md
├── docs/
│   └── project-spec.md         # 详细项目说明书
├── hf-space/
│   ├── app.py                   # Gradio 主应用（接入 Persona Engine）
│   ├── persona_engine.py        # 人格引擎（配置加载 + Prompt 构建）
│   ├── persona_config.json      # 8 参数可调配置
│   ├── admin_panel.py           # 运营后台可视化调参面板
│   ├── .env                     # API 密钥（已加入 .gitignore）
│   ├── requirements.txt
│   └── assets/
│       └── lottie/              # Lottie 动画 JSON
│           ├── burn.json
│           ├── water.json
│           └── light.json
├── models/                      # 本地模型（未来）
└── mobile-client/               # 移动端（未来）
```

---

## 🛣 路线图

```
HF MVP（当前） → 本地模型 → RAG 知识库 → 移动端 → 内测 → 正式上线
```

### 阶段一：HF MVP ✅（已完成）
- [x] Gradio 基础应用 + DeepSeek API
- [x] 主教人格 V1（固定三段式）
- [x] 情绪识别（愤怒/悲伤/迷茫）
- [x] Lottie 共鸣仪式动画
- [x] 深色琥珀主题 UI
- [x] Persona Engine V2（参数可配 + 运营后台）
- [x] 8 参数可调配置系统

### 后续阶段
- Persona Engine V3（情绪自适应）
- 本地模型（3B–4B 量化）
- RAG 圣经知识库
- Android/iOS 双端开发
- 内测与正式上线

---

## 📜 更新日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| V1.0 | - | 初始项目结构 |
| V1.1 | 2026-06-26 | AI 人格更新为主教（洞察→引导→教导）；增加情绪识别；增加 Lottie 动画 |
| V1.2 | 2026-06-26 | 增加 README 主教人格章节；整理项目结构 |
| V1.3 | 2026-06-26 | 新增 Persona Engine V2（参数可配）；新增 admin_panel.py 运营面板；新增 persona_config.json；更新项目结构 |

---

## ⚠️ 隐私声明

- **免费版（HF Space）**：所有对话通过云端 API 处理，不适合敏感内容  
- **付费版（本地运行）**：零上传、零日志，完全离线