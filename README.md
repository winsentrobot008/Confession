# Confession — AI 告解房（项目说明书 V1.4）

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

## 🕊 教父人格（Father Persona）V1.0

教父人格是 Confession 的第二人格系统，用于提供更深层的灵性洞察与智慧引导。

### ① 角色定位
- 灵性导师、洞察者、先知
- 不评判，只揭示真理
- 语言深邃、象征、经文式节奏

### ② 回复结构（固定三段式）
1. **洞见 Insight**：揭示灵性根源
2. **智慧 Wisdom**：哲理与象征
3. **先知 Prophecy**：启示性预言或方向

### ③ 示例
用户："我觉得自己不配被爱。"

教父回复格式：
```
洞见：你害怕的不是爱，而是被看见的自己。
智慧：爱不是奖赏，而是镜子。镜中映出的，是你拒绝拥抱的灵魂。
先知：当你敢于直视自己的影子，爱将不再是他人的恩赐，而是你的本性。
```

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

### V5 — 多人格切换（当前版本）
- 支持两个预设人格配置：主教（Bishop）和教父（Father）
- 用户通过 UI 下拉框一键切换人格
- 每个人格拥有独立的回复结构体系

---

## 🌍 多语言支持（Multi-Language Support）

系统支持 6 种语言：

| 语言 | 代码 | UI 文本来源 | 人格提示词来源 |
|------|------|------------|--------------|
| 中文 | zh | /locales/zh.json | /persona/father_zh.txt |
| English | en | /locales/en.json | /persona/father_en.txt |
| Svenska | sv | /locales/sv.json | /persona/father_sv.txt |
| Español | es | /locales/es.json | /persona/father_es.txt |
| 日本語 | jp | /locales/jp.json | /persona/father_jp.txt |
| 한국어 | kr | /locales/kr.json | /persona/father_kr.txt |

### UI 层
- 所有界面文本来自 `/locales/{lang}.json`
- 用户通过顶部下拉框切换语言

### LLM 层（人格提示词）
- 教父人格提示词按语言存储在 `/persona/father_{lang}.txt`
- 自动回退：若指定语言文件不存在 → 使用英文版
- 模型自动识别用户输入语言并用同语言回复

### 免费版 / 付费版多语言策略

| 维度 | 免费版（云端） | 付费版（本地） |
|------|-------------|-------------|
| 模型 | 开源模型（0 Token 成本） | 本地模型（无限制） |
| 回复长度 | 最多 300 Tokens | 最多 2000 Tokens |
| 多语言 | 基础支持 | 完整多语言人格提示词 |
| 记忆 | 无 | 灵魂画像 + 记忆数据库 |
| 人格 | 固定主教 / 教父 | 完整人格体系 |

环境变量 `CONFESSION_FREE_VERSION=true/false` 控制版本策略。

---

## 🧠 技术实现（后端）

### Persona Engine 文件结构

```
hf-space/
├── persona_engine.py         # 配置加载 + 动态 Prompt 构建引擎 + 多语言加载
├── persona_config.json       # 8 参数配置文件（可由 admin_panel 修改）
├── admin_panel.py            # 运营后台可视化调参面板
├── app.py                    # Gradio 主应用（接入 Persona Engine）
├── .env                      # API 密钥
├── assets/lottie/            # Lottie 动画 JSON
└── requirements.txt
```

### 核心代码

`persona_engine.py` 中的 `get_persona_prompt(persona, lang)` 根据人格和语言动态加载 system prompt：

```python
def get_persona_prompt(persona: str, lang: str) -> str:
    """获取指定人格和语言的完整 system prompt。"""
    lang_instruction = f"\n\n请使用用户输入的语言（{lang}）进行回复。"
    if persona == "father":
        prompt = load_persona_prompt("father", lang)
        return prompt + lang_instruction
    else:
        config = load_config()
        return build_bishop_prompt(config) + lang_instruction
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
- **人格切换**：顶部下拉框选择主教/教父人格  
- **语言切换**：顶部下拉框选择 6 种语言  

---

## 📁 项目结构

```
Confession/
├── README.md
├── locales/                     # UI 多语言文本
│   ├── zh.json
│   ├── en.json
│   ├── sv.json
│   ├── es.json
│   ├── jp.json
│   └── kr.json
├── persona/                     # 人格提示词（多语言）
│   ├── father_zh.txt
│   ├── father_en.txt
│   ├── father_sv.txt
│   ├── father_es.txt
│   ├── father_jp.txt
│   └── father_kr.txt
├── docs/
│   └── project-spec.md         # 详细项目说明书
├── hf-space/
│   ├── app.py                   # Gradio 主应用（接入 Persona Engine + 多语言）
│   ├── persona_engine.py        # 人格引擎（配置加载 + Prompt 构建 + 多语言加载）
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
- [x] 教父人格（Father Persona）V1.0
- [x] 多人格切换（主教 / 教父）
- [x] 多语言支持（6 种语言）
- [x] 免费版 / 付费版 Token 策略

### 后续阶段
- Persona Engine V3（情绪自适应）
- 本地模型（3B–4B 量化）
- RAG 圣经知识库
- Android/iOS 双端开发
- 内测与正式上线

---

## 🩺 系统版本与健康检测
- `/health`：返回服务状态 JSON。
- `/version`：返回版本号与构建时间：
  ```json
  {"service": "Confession", "version": "2.0.1", "build_time": "2026-06-26 21:08", "frontend": "Dark Mode + Halo + Speech I/O + Multi-Language"}
  ```
- `/debug`：返回当前运行时调试信息（语言、人格、模型）：
  ```json
  {"service": "Confession", "version": "2.0.1", "language": "sv", "persona": "father", "model": "deepseek-chat", "status": "running"}
  ```
- 前端版本：Dark Mode 2.0 + Halo 光圈动画 + Speech I/O 语音输入输出 + 多语言支持。
- 当 Render 健康检测路由返回 HTTP 200 时，部署被视为成功。

---

## 🧩 后端框架更新（Flask → FastAPI）

- 原 Flask 无 router 属性，导致部署失败。
- 已改为 FastAPI + Gradio 挂载。
- Render 端口绑定修复为 8000。
- 启动命令：`python app.py`

### Render 部署修复

1. 终止卡住的部署进程（Render Console → Deploys → Cancel Deploy）
2. 确认端口绑定：`server_name="0.0.0.0"`, `server_port=8000`
3. 设置环境变量：`PORT = 8000`
4. 强制重新部署：`Manual Deploy → Deploy latest commit`
5. 验证日志输出：`Running on http://0.0.0.0:8000`

## 🧩 Render 环境修复
- 错误：`Unexpected token '?.'`
- 原因：Node 版本过旧，Gradio 6 构建时依赖现代 JS 语法（可选链操作符），旧版 Node 不支持。
- 解决：在 `render.yaml` 中设置 `NODE_VERSION=20`，升级构建环境。

## 🧩 前端缓存修复
- 错误：`Unexpected token '.'`
- 原因：浏览器或 CDN 缓存旧的 Gradio 构建文件，导致 JS 语法不兼容。
- 解决：清理构建产物 + 添加 `no-cache` HTTP 中间件 + 调用 `gr.close_all()` 清理旧实例。

---

## 📜 更新日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| V1.0 | - | 初始项目结构 |
| V1.1 | 2026-06-26 | AI 人格更新为主教（洞察→引导→教导）；增加情绪识别；增加 Lottie 动画 |
| V1.2 | 2026-06-26 | 增加 README 主教人格章节；整理项目结构 |
| V1.3 | 2026-06-26 | 新增 Persona Engine V2（参数可配）；新增 admin_panel.py 运营面板；新增 persona_config.json；更新项目结构 |
| V1.4 | 2026-06-26 | 新增教父人格（Father Persona）；新增人格切换 UI；新增多语言支持（6 种语言）；新增免费版/付费版策略；新增 /locales 和 /persona 目录 |
| V1.5 | 2026-06-26 | 后端框架从 Flask 迁移至 FastAPI；修复 Render 端口绑定为 8000；Gradio 使用 mount_gradio_app 挂载 |

---

## ⚠️ 隐私声明

- **免费版（HF Space）**：所有对话通过云端 API 处理，不适合敏感内容  
- **付费版（本地运行）**：零上传、零日志，完全离线

---

## 🔐 安全说明

### 1. 后台密码保护
访问后台 `/admin` 需要密码验证。
- 密码通过环境变量 `ADMIN_PASSWORD` 设置
- 默认密码：`admin123`（请在生产环境中修改）
- 访问方式：`https://你的域名/admin?pwd=你的密码`
- 实现方式：Flask 路由 + `@require_admin_password` 装饰器

### 2. API Key 安全
- API Key 通过环境变量 `DEEPSEEK_API_KEY` 读取
- 前端（Gradio）不显示、不传递 API Key
- 日志中已移除 API Key 输出

### 3. 免费版 / 付费版环境变量
通过 `CONFESSION_FREE_VERSION=true/false` 控制 Token 策略：
- `true`（默认）→ 免费版，max_tokens=300
- `false` → 付费版，max_tokens=2000

### 4. Render 环境变量配置
在 Render Dashboard → Environment 中需添加：
```
ADMIN_PASSWORD = <自定义后台密码>
DEEPSEEK_API_KEY = <真实 DeepSeek API Key>
CONFESSION_FREE_VERSION = true
```

### 5. 本地开发
```bash
# 设置环境变量后启动
set ADMIN_PASSWORD=your_password
set DEEPSEEK_API_KEY=your_key
set CONFESSION_FREE_VERSION=true
python hf-space/app.py