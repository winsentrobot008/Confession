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