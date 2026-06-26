import gradio as gr
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "persona_config.json")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(emotion, sin, temp, style, path, length, depth, quote):
    cfg = {
        "emotion_detection": emotion,
        "sin_detection": sin,
        "language_temperature": temp,
        "teaching_style": style,
        "path_guidance": path,
        "reply_length": length,
        "question_depth": int(depth),
        "quote_style": quote
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)
    return "✅ 配置已保存"

def admin_ui():
    cfg = load_config()

    with gr.Blocks(title="Confession — 主教人格参数调节面板") as demo:
        gr.Markdown("# 🛠 主教人格参数调节面板（运营后台）")
        gr.Markdown("修改后点击「保存配置」，下次告解时将自动应用新参数。")

        with gr.Row():
            emotion = gr.Slider(0, 1, value=cfg["emotion_detection"], step=0.1, label="🔍 情绪识别强度")
            sin = gr.Slider(0, 1, value=cfg["sin_detection"], step=0.1, label="⚖️ 罪性识别强度")
            temp = gr.Slider(0, 1, value=cfg["language_temperature"], step=0.1, label="🌡️ 语言温度")
            depth = gr.Slider(1, 3, value=cfg["question_depth"], step=1, label="❓ 提问深度")

        with gr.Row():
            style = gr.Dropdown(
                ["spiritual", "gentle", "serious"],
                value=cfg["teaching_style"],
                label="📖 教导风格"
            )
            quote = gr.Dropdown(
                ["scripture", "literature", "none"],
                value=cfg["quote_style"],
                label="📜 引用风格"
            )
            length = gr.Dropdown(
                ["short", "medium", "long"],
                value=cfg["reply_length"],
                label="📏 回复长度"
            )

        path = gr.Checkbox(value=cfg["path_guidance"], label="🧭 启用灵修路径引导")

        status = gr.Textbox(label="状态", interactive=False)

        save_btn = gr.Button("💾 保存配置", variant="primary")
        save_btn.click(
            fn=save_config,
            inputs=[emotion, sin, temp, style, path, length, depth, quote],
            outputs=status
        )

        gr.Markdown("---")
        gr.Markdown("💡 **提示**：参数说明详见 `persona_engine.py` 中的 `DEFAULT_CONFIG`。")

    demo.launch()

if __name__ == "__main__":
    admin_ui()