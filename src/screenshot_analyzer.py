from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image, ImageStat

from .models import ScreenshotSummary


def analyze_screenshot(path: Optional[Path], metadata: Optional[Dict[str, str]] = None) -> ScreenshotSummary:
    if not path:
        return ScreenshotSummary(path=None, visual_hints=["未上传截图"])

    hints: List[str] = []
    if metadata:
        for key in ("screen_state", "ui_hint", "expected_visual_problem"):
            value = metadata.get(key)
            if value:
                hints.append(value)

    try:
        with Image.open(path) as image:
            width, height = image.size
            gray = image.convert("L")
            stat = ImageStat.Stat(gray)
            avg = stat.mean[0]
            extrema = gray.getextrema()
            if avg > 238 and (extrema[1] - extrema[0]) < 70:
                hints.append("截图整体接近空白，可能是白屏或渲染失败")
            if width < 900 or height < 500:
                hints.append("截图分辨率偏小，建议补充完整页面截图")
            if not hints:
                hints.append("截图已读取，可结合日志判断页面状态")
            return ScreenshotSummary(path=path, width=width, height=height, visual_hints=hints)
    except Exception as exc:
        return ScreenshotSummary(path=path, visual_hints=[f"截图读取失败：{exc}"])

