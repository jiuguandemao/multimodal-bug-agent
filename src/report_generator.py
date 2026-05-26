from pathlib import Path
from typing import Optional

from .code_locator import format_location
from .config import REPORTS_DIR, TESTS_DIR, ensure_output_dirs
from .models import BugAnalysis


def render_markdown(analysis: BugAnalysis) -> str:
    locations = "\n".join(
        f"- `{format_location(hit.path, hit.start_line, hit.end_line)}`，score={hit.score}，{hit.reason}\n\n```text\n{hit.preview}\n```"
        for hit in analysis.suspicious_locations
    ) or "- 暂未定位到具体代码位置"

    evidence = "\n".join(f"- {item}" for item in analysis.evidence)
    steps = "\n".join(f"{idx}. {step}" for idx, step in enumerate(analysis.reproduce_steps, start=1))
    fixes = "\n".join(f"- {item}" for item in analysis.fix_suggestions)
    ai_section = _render_ai_section(analysis)

    return f"""# {analysis.title}

## 缺陷摘要

- 缺陷类型：{analysis.bug_type}
- 严重程度：{analysis.severity}
- 影响模块：{analysis.affected_module}
- 分析模式：{analysis.analysis_mode}
- 规则置信度：{analysis.confidence}

{analysis.summary}

## 关键证据

{evidence}

## 复现步骤

{steps}

## 根因分析

{analysis.root_cause}

## 可疑代码位置

{locations}

## 修复建议

{fixes}

{ai_section}

## 自动生成测试用例

### pytest

```python
{analysis.tests.get("pytest", "").strip()}
```

### Playwright

```python
{analysis.tests.get("playwright", "").strip()}
```
"""


def save_outputs(case_name: str, analysis: BugAnalysis, output_root: Optional[Path] = None) -> Path:
    ensure_output_dirs()
    report_dir = (output_root / "reports") if output_root else REPORTS_DIR
    test_dir = (output_root / "tests") if output_root else TESTS_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)

    safe = _safe_name(case_name)
    report_path = report_dir / f"{safe}_bug_report.md"
    report_path.write_text(render_markdown(analysis), encoding="utf-8")
    (test_dir / f"{safe}_pytest_test.py").write_text(analysis.tests.get("pytest", ""), encoding="utf-8")
    (test_dir / f"{safe}_playwright_test.py").write_text(analysis.tests.get("playwright", ""), encoding="utf-8")
    return report_path


def _safe_name(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")


def _render_ai_section(analysis: BugAnalysis) -> str:
    insight = analysis.ai_insight
    if not insight:
        return "## AI 二次审查\n\n- 未启用。"
    if insight.status != "ok":
        return f"""## AI 二次审查

- Provider：{insight.provider}
- Model：{insight.model}
- 状态：{insight.status}
"""
    return f"""## AI 二次审查

- Provider：{insight.provider}
- Model：{insight.model}
- 状态：{insight.status}

{insight.content}
"""
