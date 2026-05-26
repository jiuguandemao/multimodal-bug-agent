from pathlib import Path
from typing import Iterable, List

from .code_locator import format_location
from .models import CodeHit, LogSignal, ScreenshotSummary, UploadedCase


def build_multimodal_context(
    case: UploadedCase,
    screenshot: ScreenshotSummary,
    signals: Iterable[LogSignal],
    suspicious_locations: Iterable[CodeHit],
    keyframes: List[Path] = None,
) -> str:
    """Build a compact evidence packet for an LLM or VLM.

    The current DeepSeek chat API is text-oriented, so image/video evidence is
    represented as structured visual metadata. A vision model can later replace
    these fields with real screenshot/keyframe captions without changing the
    downstream reasoning pipeline.
    """
    keyframes = keyframes or []
    parts = [
        "# Case",
        f"name: {case.name}",
        f"description: {case.description.strip()}",
        "",
        "# Screenshot evidence",
        f"path: {screenshot.path.as_posix() if screenshot.path else 'N/A'}",
        f"size: {screenshot.width}x{screenshot.height}",
        f"vision_status: {screenshot.vision_status}",
        f"vision_provider: {screenshot.vision_provider}",
        f"vision_model: {screenshot.vision_model}",
        f"vision_caption: {screenshot.vision_caption or 'N/A'}",
        "visual_hints:",
        *_bullet(screenshot.visual_hints),
        "",
        "# Video keyframes",
        *_bullet([path.as_posix() for path in keyframes] or ["no video/keyframes"]),
        "",
        "# Log signals",
        *_bullet([f"{s.source}:{s.line_no} {s.severity} {s.category} - {s.message}" for s in signals]),
        "",
        "# Suspicious code",
    ]
    for hit in suspicious_locations:
        parts.extend(
            [
                f"- location: {format_location(hit.path, hit.start_line, hit.end_line)}",
                f"  score: {hit.score}",
                f"  reason: {hit.reason}",
                "  preview:",
                _indent(hit.preview, "    "),
            ]
        )
    return "\n".join(parts)


def build_llm_prompt(evidence_packet: str) -> List[dict]:
    system = (
        "你是资深测试开发和缺陷定位专家。你要基于证据做审慎分析，"
        "不要编造不存在的日志、代码行或接口。输出中文 Markdown。"
    )
    user = f"""请根据下面的多模态证据包，做一次二次审查。

要求：
1. 先判断当前规则引擎结论是否可信。
2. 给出更像真实企业 Bug 单的根因分析。
3. 指出还缺哪些证据。
4. 给出 3 到 5 条高质量回归测试建议。
5. 如果证据不足，要明确说“不足”，不要硬定位。

多模态证据包：

{evidence_packet}
"""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _bullet(items: Iterable[str]) -> List[str]:
    values = [item for item in items if item]
    return [f"- {item}" for item in values] if values else ["- none"]


def _indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line for line in text.splitlines())
