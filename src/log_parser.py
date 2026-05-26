import re
from typing import Iterable, List

from .models import LogSignal


ERROR_PATTERNS = [
    ("server_error", re.compile(r"\b(500|Internal Server Error|Traceback|Exception)\b", re.I)),
    ("frontend_type_error", re.compile(r"\b(TypeError|undefined|null|Cannot read properties)\b", re.I)),
    ("timeout", re.compile(r"\b(timeout|ETIMEDOUT|504|Gateway Timeout|exceeded)\b", re.I)),
    ("permission", re.compile(r"\b(403|Forbidden|Unauthorized|permission|token|auth)\b", re.I)),
    ("upload_limit", re.compile(r"\b(413|payload too large|file too large|upload failed|multipart)\b", re.I)),
    ("data_mismatch", re.compile(r"\b(mismatch|inconsistent|amount|price|total|decimal|rounding)\b", re.I)),
    ("network", re.compile(r"\b(NetworkError|Failed to fetch|ECONNRESET|connection refused)\b", re.I)),
]

ENDPOINT_RE = re.compile(r"(/[A-Za-z0-9_./{}:-]+)")
STACK_RE = re.compile(r"([A-Za-z0-9_./\\-]+\.(?:py|js|jsx|ts|tsx|java|go))[:：](\d+)")


def parse_logs(frontend_log: str, backend_log: str) -> List[LogSignal]:
    signals: List[LogSignal] = []
    for source, text in (("frontend", frontend_log), ("backend", backend_log)):
        for line_no, line in enumerate(text.splitlines(), start=1):
            clean = line.strip()
            if not clean:
                continue
            severity = _detect_severity(clean)
            category = _detect_category(clean)
            if severity != "info" or category != "unknown":
                signals.append(
                    LogSignal(
                        severity=severity,
                        source=source,
                        message=clean,
                        line_no=line_no,
                        category=category,
                    )
                )
    return signals


def extract_keywords(description: str, signals: Iterable[LogSignal]) -> List[str]:
    words = set()
    for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}|[\u4e00-\u9fa5]{2,}", description):
        words.add(token.lower())
    for signal in signals:
        for endpoint in ENDPOINT_RE.findall(signal.message):
            words.add(endpoint.lower())
            words.update(part.lower() for part in endpoint.split("/") if len(part) >= 3)
        for path, _line in STACK_RE.findall(signal.message):
            words.add(path.replace("\\", "/").lower())
            words.add(path.rsplit("/", 1)[-1].lower())
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", signal.message):
            if token.lower() not in {"error", "warn", "info", "http", "https"}:
                words.add(token.lower())
    return sorted(words)


def summarize_signals(signals: List[LogSignal]) -> List[str]:
    summary = []
    for signal in signals[:12]:
        summary.append(f"[{signal.source}:{signal.line_no}] {signal.category} - {signal.message}")
    if len(signals) > 12:
        summary.append(f"... 还有 {len(signals) - 12} 条日志信号")
    return summary


def dominant_category(signals: List[LogSignal]) -> str:
    if not signals:
        return "unknown"
    scores = {}
    for signal in signals:
        scores[signal.category] = scores.get(signal.category, 0) + (2 if signal.severity == "error" else 1)
    return max(scores, key=scores.get)


def _detect_severity(line: str) -> str:
    if re.search(r"\b(error|fatal|exception|traceback|500|TypeError|failed)\b", line, re.I):
        return "error"
    if re.search(r"\b(warn|warning|timeout|slow|retry)\b", line, re.I):
        return "warning"
    return "info"


def _detect_category(line: str) -> str:
    for category, pattern in ERROR_PATTERNS:
        if pattern.search(line):
            return category
    return "unknown"

