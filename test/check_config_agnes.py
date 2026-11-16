"""检查 .env 配置并向 Agnes 发起一次对话

用法:
    python tmp/check_config_agnes.py
    python tmp/check_config_agnes.py "自定义问题"
"""

import json
import os
import sys
import urllib.request

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.config import get_config

config = get_config()
question = sys.argv[1] if len(sys.argv) > 1 else "用一句话介绍你自己"

print("base_url:", config.LLM_BASE_URL)
print("model   :", config.AGENS_MODEL_TEXT)
print("api_key :", f"{config.LLM_API_KEY[:6]}...{config.LLM_API_KEY[-4:]}" if len(config.LLM_API_KEY) > 10 else "未配置")

if not config.LLM_API_KEY:
    sys.exit("AGNES_API_KEY 未配置，退出")

payload = {
    "model": config.AGENS_MODEL_TEXT,
    "messages": [{"role": "user", "content": question}],
    "max_tokens": 100,
}
request = urllib.request.Request(
    config.LLM_BASE_URL.rstrip("/") + "/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.LLM_API_KEY}",
    },
)

print("提问    :", question)
with urllib.request.urlopen(request, timeout=config.EXECUTION_TIMEOUT_SECONDS) as response:
    data = json.loads(response.read().decode("utf-8"))

print("回复    :", data["choices"][0]["message"]["content"])
print("tokens  :", data.get("usage", {}).get("total_tokens"))
