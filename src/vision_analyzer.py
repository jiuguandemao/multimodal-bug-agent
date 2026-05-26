import base64
import mimetypes
import os
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

from .models import ScreenshotSummary


def enhance_screenshot_with_vision(summary: ScreenshotSummary) -> ScreenshotSummary:
    """Optionally call a VLM, such as Qwen-VL, to describe a UI screenshot.

    This function is intentionally optional. If no VLM key is configured, it
    returns the original screenshot summary and marks the vision status as
    skipped. That keeps the project runnable for reviewers without paid API
    credentials.
    """
    load_dotenv()
    if not summary.path or not summary.path.exists():
        summary.vision_status = "no_image"
        return summary

    provider = os.getenv("VISION_PROVIDER", "qwen").strip().lower()
    api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY") or os.getenv("VISION_API_KEY") or ""
    base_url = os.getenv("VISION_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1").rstrip("/")
    model = os.getenv("VISION_MODEL", "qwen3-vl-plus")

    summary.vision_provider = provider
    summary.vision_model = model

    if not api_key.strip():
        summary.vision_status = "skipped: missing VISION/QWEN API key"
        return summary

    try:
        caption = _call_openai_compatible_vlm(
            api_key=api_key,
            base_url=base_url,
            model=model,
            image_path=summary.path,
        )
        summary.vision_caption = caption
        summary.vision_status = "ok"
        if caption:
            summary.visual_hints.append(f"VLM视觉分析：{caption[:300]}")
    except Exception as exc:
        summary.vision_status = f"error: {exc}"
    return summary


def _call_openai_compatible_vlm(api_key: str, base_url: str, model: str, image_path: Path) -> str:
    mime = mimetypes.guess_type(image_path.name)[0] or "image/png"
    image_b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    data_url = f"data:{mime};base64,{image_b64}"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "你是软件测试专家。请分析这张Web页面截图，输出："
                            "1. 页面类型；2. 可见异常状态；3. 错误文案；"
                            "4. 可疑UI组件；5. 建议结合哪些日志继续定位。"
                            "不要编造截图中看不到的事实。"
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        "stream": False,
        "max_tokens": 700,
    }
    response = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=int(os.getenv("VISION_TIMEOUT_SECONDS", "60")),
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
