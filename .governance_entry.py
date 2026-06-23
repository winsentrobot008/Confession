import os
import time
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GOV = os.path.join(ROOT, "Cline-anti-freeze")

sys.path.append(GOV)

print("[Governance] Confession 项目正在接入治理体系...")

# 写入心跳
with open(".heartbeat", "w", encoding="utf-8") as f:
    f.write(str(time.time()))

print("[Governance] 心跳文件已写入")

# 引用治理链接器
try:
    import governance_linker
    governance_linker.ensure_governance()
    print("[Governance] 宪法链接器已加载")
except Exception as e:
    print("[Governance] 加载治理链接器失败:", e)

print("[Governance] Confession 已接入治理体系")