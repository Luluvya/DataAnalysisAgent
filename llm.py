"""
LLM 调用封装
支持 DeepSeek-V3 via 硅基流动
"""
import os
import httpx
from typing import Optional

SILICONFLOW_KEY = os.getenv("SILICONFLOW_KEY", "")
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
LLM_MODEL = "deepseek-ai/DeepSeek-V3"


async def llm_call(
    system: str,
    user: str,
    max_tokens: int = 2000,
    temperature: float = 0.1
) -> str:
    """调用 LLM，返回文本"""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {SILICONFLOW_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": LLM_MODEL,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ]
            }
        )
        data = resp.json()
        return data["choices"][0]["message"]["content"]
