from pathlib import Path
from typing import Iterable, List

from .models import CodeHit, CodeSnippet, LogSignal


def locate_suspicious_code(snippets: Iterable[CodeSnippet], keywords: List[str], signals: List[LogSignal], limit: int = 5) -> List[CodeHit]:
    hits: List[CodeHit] = []
    categories = {signal.category for signal in signals}
    for snippet in snippets:
        haystack = f"{snippet.path.as_posix()}\n{snippet.text}".lower()
        score = 0
        matched = []
        for keyword in keywords:
            if len(keyword) < 3:
                continue
            if keyword in haystack:
                score += 3 if keyword.startswith("/") or "." in keyword else 1
                matched.append(keyword)
        score += _category_score(categories, haystack)
        if score <= 0:
            continue
        reason = "匹配到日志/描述关键词：" + ", ".join(matched[:8]) if matched else "代码结构与错误类型相似"
        hits.append(
            CodeHit(
                path=snippet.path,
                start_line=snippet.start_line,
                end_line=snippet.end_line,
                score=score,
                reason=reason,
                preview=_preview(snippet.text),
            )
        )
    hits.sort(key=lambda item: item.score, reverse=True)
    return hits[:limit]


def _category_score(categories: set, haystack: str) -> int:
    score = 0
    if "frontend_type_error" in categories and any(token in haystack for token in ("undefined", "null", "?.", "response.data")):
        score += 4
    if "server_error" in categories and any(token in haystack for token in ("raise", "exception", "return 500", "validate")):
        score += 4
    if "timeout" in categories and any(token in haystack for token in ("timeout", "sleep", "retry", "loading")):
        score += 4
    if "permission" in categories and any(token in haystack for token in ("role", "permission", "token", "auth")):
        score += 4
    if "upload_limit" in categories and any(token in haystack for token in ("upload", "file", "max_size", "multipart")):
        score += 4
    if "data_mismatch" in categories and any(token in haystack for token in ("amount", "price", "total", "decimal", "round")):
        score += 4
    return score


def _preview(text: str, max_lines: int = 12) -> str:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:max_lines])


def format_location(path: Path, start_line: int, end_line: int) -> str:
    if start_line == end_line:
        return f"{path.as_posix()}:{start_line}"
    return f"{path.as_posix()}:{start_line}-{end_line}"

