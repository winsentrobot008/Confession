import gradio as gr
import os
import json
import requests
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from persona_engine import load_config, build_bishop_prompt, father_persona, PERSONA_LIST, get_persona_prompt

# ============================================================
# .env 加载
# ============================================================
load_dotenv(override=True)
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

# ============================================================
# 情绪识别
# ============================================================
EMOTION_KEYWORDS = {
    "angry": ["生气", "恨", "怒", "愤", "愤怒", "恼火", "暴躁", "气", "怨恨"],
    "sad": ["哭", "痛", "失望", "孤独", "悲伤", "难过", "伤心", "心碎", "绝望", "悲哀"],
    "confused": ["不知道", "困惑", "迷失", "空虚", "迷茫", "不解", "彷徨", "茫然", "疑惑", "糊涂"],
}

def detect_emotion(text: str) -> str:
    text_lower = text.lower()
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return emotion
    return "neutral"

# ============================================================
# 主告解函数（三段式 HTML 卡片输出）
# ============================================================
_current_language = "unknown"
_current_persona = "unknown"
_current_model = "unknown"

def confess(user_text, persona, lang):
    global _current_language, _current_persona, _current_model

    if not API_KEY:
        return "<div class='card'><div class='card-title'>Error</div><div>❌ 未检测到 DEEPSEEK_API_KEY</div></div>"

    emotion = detect_emotion(user_text)
    model = "deepseek-chat"
    max_tokens = 300

    _current_language = lang
    _current_persona = persona
    _current_model = model

    system_prompt = get_persona_prompt(persona, lang)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        data = response.json()
        if "choices" in data:
            content = data["choices"][0]["message"]["content"]
            # 将 AI 回复拆分为三段式卡片：Insight / Guidance / Teaching
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            insight = paragraphs[0] if len(paragraphs) > 0 else content
            guidance = paragraphs[1] if len(paragraphs) > 1 else content
            teaching = paragraphs[2] if len(paragraphs) > 2 else content
            trigger_script = "<script>if(window.__confessionParticles)window.__confessionParticles.trigger(60);</script><script>if(window.triggerHolyEnergy)window.triggerHolyEnergy();</script>"
            return f"""
            {trigger_script}
            <div class='card'>
                <div class='card-title'>Insight</div>
                <div>{insight}</div>
            </div>
            <div class='card'>
                <div class='card-title'>Guidance</div>
                <div>{guidance}</div>
            </div>
            <div class='card'>
                <div class='card-title'>Teaching</div>
                <div>{teaching}</div>
            </div>
            """
        else:
            return f"<div class='card'><div class='card-title'>Error</div><div>❌ API 返回异常：{data}</div></div>"
    except Exception as e:
        return f"<div class='card'><div class='card-title'>Error</div><div>❌ 请求失败：{e}</div></div>"

# ============================================================
# FastAPI 应用 — 静态资源挂载 & 路由
# ============================================================
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(BASE_DIR, "assets")
app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

# ============================================================
# Gradio 界面（视频背景 + 暗黑主题 + 三段式卡片输出 + 粒子特效 + 底部声明）
# ============================================================
_css_path = os.path.join(assets_path, "theme.css")
with open(_css_path, "r", encoding="utf-8") as f:
    _theme_css = f.read()

with gr.Blocks(css=_theme_css, head="""<script src="/assets/js/particles.js"></script><script src="/assets/js/energy-ring.js"></script>""") as demo:
    gr.HTML("""
    <video class='bg-video' autoplay loop muted playsinline poster='/assets/images/confession-room.jpg'>
        <source src='/assets/images/confession-room-loop.webm' type='video/webm'>
    </video>
    """)
    gr.HTML("<div class='halo'></div>")
    input_text = gr.Textbox(label="你的告解", placeholder="在这里匿名倾诉……", lines=3)
    with gr.Row():
        persona_selector = gr.Dropdown(list(PERSONA_LIST.keys()), label="人格", value="bishop")
        lang_selector = gr.Dropdown(["zh", "en", "sv", "es", "jp", "kr"], label="语言", value="zh")
    submit = gr.Button("✝️ 开始告解")
    output_text = gr.HTML(label="Response")

    submit.click(confess, [input_text, persona_selector, lang_selector], output_text)

    gr.HTML("""
    <div class='footer'>
        Confession v2.1 — Privacy First. No data stored.
    </div>
    """)

# ============================================================
# 健康检测 & 调试路由
# ============================================================
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/debug")
def debug():
    return {
        "language": _current_language,
        "persona": _current_persona,
        "model": _current_model
    }

# ============================================================
# 挂载 Gradio 应用到根路径
# ============================================================
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
