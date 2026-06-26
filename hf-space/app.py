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
    if user_is_free:
        return "deepseek-chat", 300
    else:
        return "deepseek-chat", 2000

# ============================================================
# 多语言文本加载
# ============================================================
LOCALES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "locales")

def load_locale(lang: str) -> dict:
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
    text_lower = text.lower()
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return emotion
    return "neutral"

def emotion_to_cn(emotion: str) -> str:
    mapping = {"angry": "愤怒", "sad": "悲伤", "confused": "迷茫", "neutral": "平静"}
    return mapping.get(emotion, "平静")

def emotion_to_lottie(emotion: str) -> str:
    mapping = {"angry": "burn", "sad": "water", "confused": "light"}
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
        return "<div style='width:128px;height:128px;margin:0 auto;background:rgba(20,20,22,0.6);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#6F6F6F;font-size:12px;'>—</div>"
    lottie_json = json.dumps(lottie_dict)
    return f"""
    <div id="lottie-container" style="width:128px;height:128px;margin:0 auto;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
    <script>
        (function() {{
            var c = document.getElementById('lottie-container');
            if (!c) return;
            c.innerHTML = '';
            var animData = {lottie_json};
            lottie.loadAnimation({{
                container: c,
                renderer: 'svg',
                loop: false,
                autoplay: true,
                animationData: animData
            }});
        }})();
    </script>
    """

# ============================================================
# 全局暗黑主题 CSS + 光圈动画 + 手机优先 + 语音按钮
# ============================================================
GLOBAL_CSS = """
/* ========== 全局暗黑风格 ========== */
:root {
    --bg-primary: #0D0D0F;
    --bg-secondary: #111214;
    --bg-card: rgba(20, 20, 22, 0.8);
    --text-primary: #EDEDED;
    --text-secondary: #A0A0A0;
    --text-muted: #6F6F6F;
    --gold: #C9A86A;
    --gold-soft: #E8D9B5;
    --gold-light: #F5E6C8;
    --border-subtle: rgba(255, 255, 255, 0.08);
    --radius: 12px;
}

* { box-sizing: border-box; }

body {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    margin: 0;
    padding: 0;
}

/* Gradio 容器覆盖 */
.gradio-container,
.wrap,
#main,
.gr-box,
.gr-block,
.gr-form,
.panel,
.tab-nav,
.tabitem {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* 卡片容器 */
.card,
.gr-box,
[class*="panel"] {
    background: var(--bg-card) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border-subtle) !important;
    padding: 16px !important;
    transition: box-shadow 0.3s ease;
}
.card:hover,
.gr-box:hover {
    box-shadow: 0 0 18px rgba(201, 168, 106, 0.15);
}

/* 输入框 */
input, textarea, .gr-input, .gr-textarea {
    background: #151518 !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-size: 15px !important;
    padding: 12px 14px !important;
    outline: none !important;
    transition: border 0.3s, box-shadow 0.3s;
}
input:focus, textarea:focus, .gr-input:focus-within, .gr-textarea:focus-within {
    border-bottom: 2px solid var(--gold) !important;
    box-shadow: 0 0 12px rgba(201, 168, 106, 0.4) !important;
}

/* 按钮 */
button, .gr-button {
    background: linear-gradient(135deg, #1a1a1e, #222226) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius) !important;
    color: var(--gold) !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
}
button:hover, .gr-button:hover {
    border-color: var(--gold) !important;
    box-shadow: 0 0 16px rgba(201, 168, 106, 0.3) !important;
    background: linear-gradient(135deg, #222226, #2a2a2e) !important;
}

/* Radio 标签 */
label, .gr-radio, .gr-form-label {
    color: var(--text-secondary) !important;
    font-size: 13px !important;
}

/* 标题 / Markdown */
h1, h2, h3, h4, .gr-markdown h1, .gr-markdown h2, .gr-markdown h3 {
    color: var(--text-primary) !important;
}
.gr-markdown {
    color: var(--text-secondary) !important;
}

/* 链接 */
a {
    color: var(--gold) !important;
    text-decoration: none !important;
}
a:hover {
    color: var(--gold-light) !important;
    text-decoration: underline !important;
}

/* ========== Mobile First 响应式 ========== */
@media (max-width: 640px) {
    body { padding: 0 8px !important; }
    .card, .gr-box { padding: 12px !important; }
    input, textarea { font-size: 16px !important; }
    button { width: 100% !important; }
    .halo-container { padding: 16px 0 !important; }
    .halo { width: 80px !important; height: 80px !important; }
}

@media (min-width: 641px) and (max-width: 1024px) {
    body { padding: 0 24px !important; }
}

@media (min-width: 1025px) {
    body { padding: 0 48px !important; max-width: 800px !important; margin: 0 auto !important; }
}

/* ========== 思考光圈（八卦双环） ========== */
.halo-container {
    display: none;
    justify-content: center;
    align-items: center;
    padding: 20px 0;
    transition: opacity 0.3s ease;
}
.halo-container.active {
    display: flex;
}

.halo {
    width: 100px;
    height: 100px;
    border: 2px solid rgba(201, 168, 106, 0.6);
    border-radius: 50%;
    position: relative;
    animation: spin 6s linear infinite, glow 2s ease-in-out infinite;
    box-shadow: 0 0 20px rgba(201, 168, 106, 0.4);
}

.halo::before {
    content: "";
    position: absolute;
    inset: 12px;
    border-radius: 50%;
    border: 1px dashed rgba(201, 168, 106, 0.5);
    animation: spin-inner 10s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
@keyframes spin-inner {
    from { transform: rotate(360deg); }
    to { transform: rotate(0deg); }
}
@keyframes glow {
    0% { box-shadow: 0 0 10px rgba(201, 168, 106, 0.2); }
    50% { box-shadow: 0 0 28px rgba(201, 168, 106, 0.7); }
    100% { box-shadow: 0 0 10px rgba(201, 168, 106, 0.2); }
}

/* 底部固定隐私条 */
.privacy-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(13, 13, 15, 0.95);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-top: 1px solid rgba(201, 168, 106, 0.15);
    padding: 10px 16px;
    text-align: center;
    font-size: 12px;
    color: #6F6F6F;
    z-index: 999;
    line-height: 1.5;
}
.privacy-bar a {
    color: #C9A86A;
    text-decoration: none;
}
.privacy-bar a:hover {
    text-decoration: underline;
}

/* 语音按钮 */
.voice-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50% !important;
    padding: 0 !important;
    font-size: 18px !important;
    background: rgba(20,20,22,0.9) !important;
    border: 1px solid var(--border-subtle) !important;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: unset !important;
}
.voice-btn:hover {
    border-color: var(--gold) !important;
    box-shadow: 0 0 14px rgba(201, 168, 106, 0.3) !important;
}
.voice-btn.listening {
    border-color: #ff4444 !important;
    box-shadow: 0 0 20px rgba(255, 68, 68, 0.4) !important;
    animation: pulse-mic 1.2s ease-in-out infinite;
}
@keyframes pulse-mic {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}
"""

# ============================================================
# 主告解函数
# ============================================================
def confess(user_text, persona, lang):
    if not API_KEY:
        return "❌ 未检测到 DEEPSEEK_API_KEY，请在 .env 中设置。", "<div style='text-align:center;color:#6F6F6F;'>请先设置 API Key</div>"

    # 1. 情绪分析
    emotion = detect_emotion(user_text)
    emotion_cn = emotion_to_cn(emotion)
    lottie_name = emotion_to_lottie(emotion)

    # 2. 获取模型和 Token 限制
    model, max_tokens = get_model_and_max_tokens(IS_FREE_VERSION)

    # 3. 构造 AI 请求
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
            ai_reply = data["choices"][0]["message"]["content"]
        else:
            ai_reply = f"❌ API 返回异常：{data}"
    except Exception as e:
        ai_reply = f"❌ 请求 DeepSeek API 失败：{e}"

    # 4. 情绪共鸣提示（不硬编码语言，让 AI 自己处理情感前缀）
    full_reply = ai_reply

    return full_reply, lottie_html(load_lottie(lottie_name), lottie_name)


# ============================================================
# Gradio 界面
# ============================================================
LANG_CHOICES = ["zh", "en", "sv", "es", "jp", "kr"]

with gr.Blocks(
    title="Confession — AI 告解房",
    theme=gr.themes.Soft(primary_hue="amber", neutral_hue="slate"),
    css=GLOBAL_CSS
) as demo:
    gr.HTML("<a href='/admin' style='display:none;'>admin</a>")

    # ---- 全局暗黑主题 + 光圈动画 + 语音 JS ----
    gr.HTML("""
    <!-- 语音识别与语音合成 JavaScript -->
    <script>
    // ========== 语音输入 ==========
    window.startVoiceInput = function() {
        var btn = document.getElementById('mic-btn');
        if (!btn) return;
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('您的浏览器不支持语音识别，请使用 Chrome。');
            return;
        }
        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        var recognition = new SpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.interimResults = false;
        recognition.continuous = false;

        btn.classList.add('listening');
        btn.textContent = '🔴';

        recognition.onresult = function(event) {
            var transcript = event.results[0][0].transcript;
            // 找到 Gradio 输入框并填入
            var textarea = document.querySelector('textarea');
            if (textarea) {
                textarea.value = transcript;
                // 触发 input 事件让 Gradio 检测到变化
                var evt = new Event('input', { bubbles: true });
                textarea.dispatchEvent(evt);
            }
            btn.classList.remove('listening');
            btn.textContent = '🎤';
        };

        recognition.onerror = function() {
            btn.classList.remove('listening');
            btn.textContent = '🎤';
        };

        recognition.onend = function() {
            btn.classList.remove('listening');
            btn.textContent = '🎤';
        };

        recognition.start();
    };

    // ========== 语音输出（朗读） ==========
    window.speakReply = function() {
        var outBox = document.querySelector('[data-testid="textbox"]');
        if (!outBox) outBox = document.querySelector('textarea');
        // 尝试从输出区域找文本
        var el = document.getElementById('reply-text');
        var text = '';
        if (el) {
            text = el.innerText || el.textContent;
        } else {
            var allTextareas = document.querySelectorAll('textarea');
            if (allTextareas.length > 1) {
                text = allTextareas[allTextareas.length - 1].value;
            }
        }
        if (!text) return;
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        var utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        window.speechSynthesis.speak(utterance);
    };

    // ========== 思考光圈控制 ==========
    window.showThinking = function() {
        var h = document.getElementById('thinking-halo');
        if (h) h.classList.add('active');
    };
    window.hideThinking = function() {
        var h = document.getElementById('thinking-halo');
        if (h) h.classList.remove('active');
    };

    // 监听输出变化自动隐藏光圈
    document.addEventListener('DOMContentLoaded', function() {
        var observer = new MutationObserver(function() {
            var outBox = document.querySelector('[data-testid="textbox"]');
            if (outBox && outBox.value && outBox.value.length > 5) {
                window.hideThinking();
            }
        });
        var target = document.querySelector('.gradio-container');
        if (target) {
            observer.observe(target, { childList: true, subtree: true, characterData: true });
        }
    });
    </script>
    """)

    # ---- 标题 ----
    gr.Markdown("""
    <div style="text-align:center;padding:8px 0 0 0;">
        <div style="font-size:28px;font-weight:700;color:#EDEDED;letter-spacing:2px;">🕯️ Confession</div>
        <div style="font-size:13px;color:#A0A0A0;margin-top:2px;">AI 告解房 · 匿名倾诉 · 灵性共鸣</div>
    </div>
    """)

    # ---- 思考光圈（隐含） ----
    thinking_halo = gr.HTML("""
    <div id="thinking-halo" class="halo-container">
        <div class="halo"></div>
    </div>
    """)

    # ---- 选择器行 ----
    with gr.Row(equal_height=True):
        lang_selector = gr.Radio(
            LANG_CHOICES,
            label="语言",
            value="zh",
            scale=1
        )
        persona_selector = gr.Radio(
            list(PERSONA_LIST.keys()),
            label="人格",
            info="主教·洞察引导教导　｜　教父·洞见智慧先知",
            value="bishop",
            scale=2
        )

    # ---- 输入区域（含语音按钮） ----
    with gr.Row():
        inp = gr.Textbox(
            lines=3,
            label="你的告解",
            placeholder="在这里匿名倾诉……",
            scale=5
        )
        mic_btn = gr.HTML(
            """<button id="mic-btn" class="voice-btn" onclick="window.startVoiceInput()" title="语音输入">🎤</button>"""
        )

    # ---- 提交按钮 ----
    btn = gr.Button("✝️ 开始告解", variant="primary", size="lg")

    # ---- 输出区域（含朗读按钮） ----
    with gr.Row():
        out = gr.Textbox(
            lines=8,
            label="AI 回复",
            elem_id="reply-text",
            scale=4
        )
        with gr.Column(scale=1, min_width=50):
            speak_btn = gr.HTML(
                """<button class="voice-btn" onclick="window.speakReply()" title="朗读回复" style="margin-top:28px;">🔊</button>"""
            )

    # ---- 仪式动画 ----
    anim = gr.HTML(label="情绪共鸣动画")

    # ---- 按钮点击：先显示光圈，再调后端 ----
    btn.click(
        js="window.showThinking();",
        fn=confess,
        inputs=[inp, persona_selector, lang_selector],
        outputs=[out, anim],
    )

    # ---- 信息提示 ----
    gr.Markdown("---")
    gr.Markdown("""
    <div style="display:flex;flex-wrap:wrap;gap:8px;font-size:13px;color:#A0A0A0;justify-content:center;">
        <span>🔥 愤怒</span>
        <span>💧 悲伤</span>
        <span>✨ 迷茫</span>
        <span>🎤 语音输入</span>
        <span>🔊 朗读回复</span>
        <span>🌐 6 种语言</span>
    </div>
    """)

    # ---- 底部固定隐私条 ----
    gr.HTML("""
    <div class="privacy-bar">
        ⚠️ <strong>免责声明：</strong>当前为云端 MVP，所有对话通过 API 处理，<strong>不适合敏感内容</strong>。
        数据不会持久存储。升级
        <a href="https://github.com/winsentrobot008/Confession" target="_blank">本地版（离线 AI 教父）</a>
        可获得完全隐私保护 · 
        <a href="/docs/privacy-policy.md" target="_blank">隐私政策</a>
        &nbsp;·&nbsp; © Confession Project
    </div>
    """)


# ============================================================
# Flask 应用 — 提供密码保护的 /admin 路由
# ============================================================
app = Flask(__name__)

@app.route("/admin")
@require_admin_password
def admin():
    launch_admin()
    return """
    <html>
    <head><title>Admin Panel</title></head>
    <body style="background:#0D0D0F;color:#EDEDED;font-family:sans-serif;text-align:center;padding:2rem;">
        <h1>🛠 Admin Panel</h1>
        <p>Admin panel launched on <strong>port 7861</strong>.</p>
        <p><a href="http://localhost:7861" target="_blank">Open Admin Panel (localhost:7861)</a></p>
        <hr>
        <p><a href="/">← Back to Confession</a></p>
    </body>
    </html>
    """

app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == '__main__':
    if "admin" in sys.argv:
        launch_admin()
    else:
        app.run(server_name="0.0.0.0", server_port=8080)