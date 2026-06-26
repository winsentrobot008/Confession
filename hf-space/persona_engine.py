import json
import os

DEFAULT_CONFIG = {
    "emotion_detection": 1.0,
    "sin_detection": 0.8,
    "language_temperature": 0.3,
    "teaching_style": "spiritual",
    "path_guidance": True,
    "reply_length": "short",
    "question_depth": 2,
    "quote_style": "scripture"
}

# ============================================================
# 教父人格（Father Persona）V1.0
# ============================================================
father_persona = {
    "name": "Father",
    "description": "灵性导师、洞察者、先知。提供洞见、智慧、启示，引导用户自省与觉醒。",
    "system_prompt": None  # Dynamically loaded via load_persona_prompt()
}

# 可用人格列表
PERSONA_LIST = {
    "bishop": {
        "name": "主教（Bishop）",
        "description": "温柔、智慧、洞察人心的主教。回复结构为洞察→引导→教导。"
    },
    "father": {
        "name": "教父（Father）",
        "description": "灵性导师、洞察者、先知。回复结构为洞见→智慧→先知。"
    }
}

# ============================================================
# 多语言人格提示词加载
# ============================================================
def load_persona_prompt(persona: str, lang: str) -> str:
    """从 /persona 目录加载对应语言的人格提示词文件。
    文件命名规则：{persona}_{lang}.txt
    如果指定语言的文件不存在，回退到英文版。
    """
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "persona")
    path = os.path.join(base_dir, f"{persona}_{lang}.txt")
    if not os.path.exists(path):
        path = os.path.join(base_dir, f"{persona}_en.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_persona_prompt(persona: str, lang: str) -> str:
    """获取指定人格和语言的完整 system prompt。
    对 bishop 人格仍使用原 build_bishop_prompt()，但附加语言指令。
    对 father 人格从外部文件加载。
    """
    lang_instruction = f"\n\n请使用用户输入的语言（{lang}）进行回复。"

    if persona == "father":
        prompt = load_persona_prompt("father", lang)
        return prompt + lang_instruction
    else:
        config = load_config()
        return build_bishop_prompt(config) + lang_instruction


def load_config():
    if os.path.exists("persona_config.json"):
        with open("persona_config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CONFIG

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