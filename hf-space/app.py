import gradio as gr
import os
import json
import requests
import subprocess
import sys
from functools import wraps
from flask import Flask, request
from dotenv import load_dotenv
from persona_engine import load_config, build_bishop_prompt, father_persona, PERSONA_LIST, get_persona_prompt

# ============================================================
# 简单安全认证 - 密码保护 Admin 面板
# ============================================================
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def require_admin_password(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pwd = request.args.get("pwd")
        if pwd != ADMIN_PASSWORD:
            return "Unauthorized: missing or wrong password", 401
        return func(*args, **kwargs)
    return wrapper

# ============================================================
# Admin 面板启动（子进程，端口 7861）
# ============================================================
def launch_admin():
    admin_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin_panel.py")
    subprocess.Popen(["python", admin_script])
    print("🛠 Admin panel launched (port 7861)")

# ============================================================
# .env 加载（支持 HF Space 环境变量）
# ============================================================
load_dotenv(override=True)

env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

# ============================================================
# 免费版 / 付费版策略（保护 Token）
# ============================================================
IS_FREE_VERSION = os.getenv("CONFESSION_FREE_VERSION", "true").lower() == "true"

def get_model_and_max_tokens(user_is_free: bool = True):
    """根据版本返回模型名称和最大 Token 数"""
    if user_is_free:
        return "deepseek-chat", 300
    else:
        return "deepseek-chat", 2000

# ============================================================
# 多语言文本加载
# ============================================================
LOCALES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "locales")

def load_locale(lang: str) -> dict:
    """从 /locales 目录加载对应语言的 UI 文本"""
    path = os.path.join(LOCALES_DIR, f"{lang}.json")
    if not os.path.exists(path):
        path = os.path.join(LOCALES_DIR, "en.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "title": "Confession",
            "start_button": "Start Confession",
            "input_placeholder": "Enter your confession...",
            "persona_label": "Choose Persona Mode",
            "language_label": "Select Language"
        }

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

        anim.addEventListener('complete', function() {{
            container.classList.add('fade-out');
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
def confess(user_text, persona, lang):
    if not API_KEY:
        return "❌ 未检测到 DEEPSEEK_API_KEY，请在 .env 中设置。", "<div>请先设置 API Key</div>"

    # 1. 情绪分析
    emotion = detect_emotion(user_text)
    emotion_cn = emotion_to_cn(emotion)
    lottie_name = emotion_to_lottie(emotion)

    # 2. 获取模型和 Token 限制（免费版 / 付费版策略）
    model, max_tokens = get_model_and_max_tokens(IS_FREE_VERSION)

    # 3. 构造 AI 请求（Persona Engine 动态提示词 + 多语言）
    system_prompt = get_persona_prompt(persona, lang)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_text
            }
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
            ai_reply = data["choices"][0]["message"]["content"]
        else:
            ai_reply = f"❌ API 返回异常：{data}"

    except Exception as e:
        ai_reply = f"❌ 请求 DeepSeek API 失败：{e}"

    # 4. 在 AI 回复前加入情绪共鸣提示（非 neutral 才加）
    if emotion != "neutral":
        full_reply = f"我感受到你的{emotion_cn}，孩子，让我们一起面对。\n\n{ai_reply}"
    else:
        full_reply = ai_reply

    # 5. 返回 AI 回复 + 对应情绪的动画
    return full_reply, lottie_html(load_lottie(lottie_name), lottie_name)


# ============================================================
# Gradio 界面
# ============================================================
LANG_CHOICES = ["zh", "en", "sv", "es", "jp", "kr"]

with gr.Blocks(title="Confession — MVP (DeepSeek + Lottie)") as demo:
    gr.HTML("<a href='/admin' style='display:none;'>admin</a>")

    # 仪式光环动画
    gr.HTML("""
    <style>
        .halo {
            width: 120px;
            height: 120px;
            border: 2px solid rgba(255, 215, 130, 0.6);
            border-radius: 50%;
            animation: spin 6s linear infinite, glow 2s ease-in-out infinite;
            box-shadow: 0 0 20px rgba(255, 215, 130, 0.4);
            margin: 0 auto 16px auto;
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        @keyframes glow {
            0% { box-shadow: 0 0 10px rgba(255, 215, 130, 0.2); }
            50% { box-shadow: 0 0 25px rgba(255, 215, 130, 0.6); }
            100% { box-shadow: 0 0 10px rgba(255, 215, 130, 0.2); }
        }
    </style>
    <div class="halo"></div>
    """)

    gr.Markdown("# 🕯️ Confession — AI 告解房（多语言版）")
    gr.Markdown("匿名倾诉 · 情绪识别 · 共鸣动画 · 多人格 · 多语言")

    with gr.Row():
        lang_selector = gr.Radio(
            LANG_CHOICES,
            label="选择语言 / Language",
            value="zh"
        )
        persona_selector = gr.Radio(
            list(PERSONA_LIST.keys()),
            label="选择人格模式",
            info="主教：洞察→引导→教导　｜　教父：洞见→智慧→先知",
            value="bishop"
        )

    inp = gr.Textbox(lines=6, label="你的告解", placeholder="请输入你的告解...")
    btn = gr.Button("开始告解")

    with gr.Row():
        out = gr.Textbox(lines=10, label="AI 回复")
        anim = gr.HTML(label="仪式动画")

    btn.click(confess, inputs=[inp, persona_selector, lang_selector], outputs=[out, anim])

    gr.Markdown("---")
    gr.Markdown("💡 **情绪识别**：系统自动识别你的情绪（愤怒🔥 / 悲伤💧 / 迷茫✨），匹配动画效果。")
    gr.Markdown("💡 **人格切换**：可选择「主教人格」或「教父人格」。")
    gr.Markdown("💡 **多语言支持**：中文 / English / Svenska / Español / 日本語 / 한국어")
    gr.Markdown("⚠️ **隐私提示：当前为云端 MVP，不适合敏感内容。**")
    gr.Markdown("[升级本地版（离线 AI 教父）](https://github.com/winsentrobot008/Confession)")


# ============================================================
# Flask 应用 — 提供密码保护的 /admin 路由
# ============================================================
app = Flask(__name__)

@app.route("/admin")
@require_admin_password
def admin():
    """密码保护的 Admin 面板入口 —— 启动子进程并引导用户访问"""
    launch_admin()
    return """
    <html>
    <head><title>Admin Panel</title></head>
    <body style="font-family: sans-serif; text-align: center; padding: 2rem;">
        <h1>🛠 Admin Panel</h1>
        <p>Admin panel launched on <strong>port 7861</strong>.</p>
        <p><a href="http://localhost:7861" target="_blank">Open Admin Panel (localhost:7861)</a></p>
        <hr>
        <p><a href="/">← Back to Confession</a></p>
    </body>
    </html>
    """

# 将 Gradio 应用挂载到 Flask 的根路径
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == '__main__':
    if "admin" in sys.argv:
        launch_admin()
    else:
        app.run(server_name="0.0.0.0", server_port=8080)