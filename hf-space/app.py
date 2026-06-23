import gradio as gr
import os
import json
import requests

API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

# 读取 Lottie 动画
def load_lottie(name):
    path = f"assets/lottie/{name}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def confess(user_text):
    if not API_KEY:
        return "❌ 未检测到 DEEPSEEK_API_KEY，请在 .env 中设置。", None

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
            reply = data["choices"][0]["message"]["content"]
        else:
            reply = f"❌ API 返回异常：{data}"

    except Exception as e:
        reply = f"❌ 请求 DeepSeek API 失败：{e}"

    # 返回 AI 回复 + 播放动画
    return reply, load_lottie("burn")


with gr.Blocks(title="Confession — MVP (DeepSeek + Lottie)") as demo:
    gr.Markdown("# 🕯️ Confession — AI 告解房（MVP）")
    gr.Markdown("匿名倾诉 · 仪式感 · 情绪释放")

    inp = gr.Textbox(lines=6, label="你的告解", placeholder="在这里匿名倾诉……")
    btn = gr.Button("开始告解")

    with gr.Row():
        out = gr.Textbox(lines=10, label="AI 教父回复")
        anim = gr.AnimatedImage(label="仪式动画")

    btn.click(confess, inputs=inp, outputs=[out, anim])

    gr.Markdown("---")
    gr.Markdown("⚠️ **隐私提示：当前为云端 MVP，不适合敏感内容。**")
    gr.Markdown("[升级本地版（离线 AI 教父）](https://github.com/winsentrobot008/Confession)")

if __name__ == '__main__':
    demo.launch()