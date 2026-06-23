import gradio as gr
import json
import os
from openai import OpenAI

# Load config
with open("model_config.json", "r") as f:
    config = json.load(f)

client = OpenAI(
    api_key=os.getenv("HF_TOKEN"),
    base_url=config.get("api_base_url", "https://api.openai.com/v1")
)

system_prompt = """You are an AI Confessor — a wise, empathetic, and non-judgmental listener.
Users come to you to confess their thoughts anonymously.
Listen with compassion, offer gentle guidance when appropriate,
and never criticize or shame. Keep responses concise (2-3 sentences).
Speak in the same language as the user's confession."""

def confess(message, history):
    messages = [{"role": "system", "content": system_prompt}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        if h[1]:
            messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=config.get("model", "gpt-4o-mini"),
        messages=messages,
        max_tokens=300
    )
    reply = response.choices[0].message.content
    return reply

with gr.Blocks(title="Confession — AI Confession Booth", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🙏 Confession — Anonymous AI Confession Booth
        *Pour out your heart in complete anonymity.*
        """
    )
    chatbot = gr.ChatInterface(
        fn=confess,
        title="Confession",
        description="Write your confession below. No judgment, just compassion.",
        theme="soft",
    )
    gr.Markdown(
        """
        ---
        ⚠️ **Disclaimer**: This is an anonymous AI service. No personal data is stored.
        For full privacy, try our [local offline version](#).
        """
    )

if __name__ == "__main__":
    demo.launch()