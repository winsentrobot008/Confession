# HF Space 部署指南

## 前提条件

- Hugging Face 账号
- 已安装 Git LFS（用于模型文件）

## 部署步骤

1. **克隆 Space 仓库**
   ```bash
   git clone https://huggingface.co/spaces/<username>/confession
   cd confession
   ```

2. **复制项目文件**
   将 `Confession/hf-space/` 下的所有文件复制到 Space 根目录。

3. **配置 Secrets**
   在 HF Space 设置中添加：
   - `HF_TOKEN` — 模型访问令牌
   - `API_MODEL` — 云端模型名称（默认：gpt-4o-mini）

4. **构建与启动**
   Space 会自动检测 `requirements.txt` 并安装依赖。

5. **验证**
   访问 `https://huggingface.co/spaces/<username>/confession` 确认正常运行。

## 目录结构说明

```
hf-space/
├── app.py              # 主应用入口（Gradio）
├── requirements.txt    # Python 依赖
├── model_config.json   # 模型配置
└── assets/
    ├── ui/             # UI 资源文件
    └── lottie/         # Lottie 动画文件