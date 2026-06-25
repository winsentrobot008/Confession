import gradio as gr
import os
import json
import requests

API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

# ============================================================
# 情绪识别词典
# ============================================================
EMOTION_KEYWORDS = {
    "angry": ["生气", "恨", "怒", "愤", "愤怒", "恼火", "暴躁", "气", "怨恨"],
    "sad": ["哭", "痛", "失望", "孤独", "悲伤", "难过", "伤心", "心碎", "绝望", "悲哀"],
    "confused": ["不知道", "困惑", "迷失", "空虚", "迷茫", "不解", "彷徨", "茫然", "疑惑", "糊涂"],
}

def detect_emotion(text: str) -> str:
    """基于关键词匹配检测情绪类型，返回 'angry' / 'sad' / 'confused' / 'neutral'"""
    text_lower = text.lower()
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return emotion
    return "neutral"

def emotion_to_cn(emotion: str) -> str:
    mapping = {
        "angry": "愤怒",
        "sad": "悲伤",
        "confused": "迷茫",
        "neutral": "平静",
    }
    return mapping.get(emotion, "平静")

def emotion_to_lottie(emotion: str) -> str:
    mapping = {
        "angry": "burn",
        "sad": "water",
        "confused": "light",
    }
    return mapping.get(emotion, "burn")

# ============================================================
# Lottie 动画
# ============================================================
def load_lottie(name):
    path = f"assets/lottie/{name}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def lottie_html(lottie_dict, animation_name="burn"):
    if not lottie_dict:
        return "<div style='width:256px;height:256px;background:#f5f5f5;border-radius:16px;display:flex;align-items:center;justify-content:center;color:#999;font-size:14px;'>暂无动画</div>"
    lottie_json = json.dumps(lottie_dict)
    # 淡入淡出 CSS: 动画开始时淡入，结束后淡出
    fade_css = """
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.8); }
            to   { opacity: 1; transform: scale(1); }
        }
        @keyframes fadeOut {
            from { opacity: 1; transform: scale(1); }
            to   { opacity: 0; transform: scale(1.2); }
        }
        .lottie-wrapper {
            width: 256px;
            height: 256px;
            margin: 0 auto;
            animation: fadeIn 0.6s ease-out forwards;
        }
        .lottie-wrapper.fade-out {
            animation: fadeOut 0.8s ease-in forwards;
        }
    </style>
    """
    return f"""{fade_css}
    <div id="lottie-container" class="lottie-wrapper"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
    <script>
        var container = document.getElementById('lottie-container');
        container.classList.remove('fade-out');

        var animData = {lottie_json};
        var anim = lottie.loadAnimation({{
            container: container,
            renderer: 'svg',
            loop: false,
            autoplay: true,
            animationData: animData
        }});

        // 动画播放完成后淡出
        anim.addEventListener('complete', function() {{
            container.classList.add('fade-out');
            // 淡出完成后重新播放（循环效果）
            setTimeout(function() {{
                container.classList.remove('fade-out');
                anim.goToAndPlay(0);
            }}, 1000);
        }});
    </script>
    """

# ============================================================
# 主告解函数
# ============================================================
def confess(user_text):
    if not API_KEY:
        return "❌ 未检测到 DEEPSEEK_API_KEY，请在 .env 中设置。", "<div>请先设置 API Key</div>"

    # 1. 情绪分析
    emotion = detect_emotion(user_text)
    emotion_cn = emotion_to_cn(emotion)
    lottie_name = emotion_to_lottie(emotion)

    # 2. 构造 AI 请求
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "你是一位温柔、耐心、无评判的 AI 教父。你的任务是倾听、安抚、引导用户释放情绪。"
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        "temperature": 0.7
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        data = response.json()

        if "choices" in data:
            ai_reply = data["choices"][0]["message"]["content"]
        else:
            ai_reply = f"❌ API 返回异常：{data}"

    except Exception as e:
        ai_reply = f"❌ 请求 DeepSeek API 失败：{e}"

    # 3. 在 AI 回复前加入情绪共鸣提示（非 neutral 才加）
    if emotion != "neutral":
        full_reply = f"我感受到你的{emotion_cn}，孩子，让我们一起面对。\n\n{ai_reply}"
    else:
        full_reply = ai_reply

    # 4. 返回 AI 回复 + 对应情绪的动画
    return full_reply, lottie_html(load_lottie(lottie_name), lottie_name)


# ============================================================
# Gradio 界面
# ============================================================
with gr.Blocks(title="Confession — MVP (DeepSeek + Lottie)") as demo:
    gr.Markdown("# 🕯️ Confession — AI 告解房（视觉增强版）")
    gr.Markdown("匿名倾诉 · 仪式感 · 情绪识别 · 共鸣动画")

    inp = gr.Textbox(lines=6, label="你的告解", placeholder="在这里匿名倾诉……")
    btn = gr.Button("开始告解")

    with gr.Row():
        out = gr.Textbox(lines=10, label="AI 教父回复")
        anim = gr.HTML(label="仪式动画")

    btn.click(confess, inputs=inp, outputs=[out, anim])

    gr.Markdown("---")
    gr.Markdown("💡 **情绪识别**：系统会自动识别你的情绪（愤怒🔥 / 悲伤💧 / 迷茫✨），匹配相应的动画效果。")
    gr.Markdown("⚠️ **隐私提示：当前为云端 MVP，不适合敏感内容。**")
    gr.Markdown("[升级本地版（离线 AI 教父）](https://github.com/winsentrobot008/Confession)")

if __name__ == '__main__':
    demo.launch(theme=gr.themes.Soft(
        primary_hue="amber",
        secondary_hue="neutral",
        neutral_hue="stone",
        font=gr.themes.GoogleFont("Merriweather"),
    ))