import argparse
import json
from pathlib import Path

from src.bug_reasoner import analyze_case
from src.config import EXAMPLES_DIR
from src.models import UploadedCase
from src.report_generator import save_outputs


def load_case(case_dir: Path) -> UploadedCase:
    metadata_path = case_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    video_path = None
    for candidate in ("operation.mp4", "operation.gif"):
        if (case_dir / candidate).exists():
            video_path = case_dir / candidate
            break
    return UploadedCase(
        name=metadata.get("name", case_dir.name),
        description=(case_dir / "description.txt").read_text(encoding="utf-8"),
        screenshot_path=case_dir / "screenshot.png",
        video_path=video_path,
        frontend_log=(case_dir / "frontend.log").read_text(encoding="utf-8"),
        backend_log=(case_dir / "backend.log").read_text(encoding="utf-8"),
        code_root=case_dir / "code",
        metadata=metadata,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MultiBug-Agent on a demo case.")
    parser.add_argument("--case", default="case_01_register_500", help="Example case folder name.")
    parser.add_argument("--use-llm", action="store_true", help="Enable optional DeepSeek/OpenAI-compatible LLM enhancement.")
    args = parser.parse_args()

    case_dir = EXAMPLES_DIR / args.case
    if not case_dir.exists():
        available = ", ".join(path.name for path in sorted(EXAMPLES_DIR.glob("case_*")))
        raise SystemExit(f"Case not found: {case_dir}\nAvailable cases: {available}")

    case = load_case(case_dir)
    analysis = analyze_case(case, use_llm=args.use_llm)
    report_path = save_outputs(case.name, analysis)
    print(f"分析完成：{analysis.title}")
    print(f"缺陷类型：{analysis.bug_type}")
    print(f"报告已生成：{report_path}")
    if analysis.ai_insight:
        print(f"AI 二次审查：{analysis.ai_insight.status}")
        print(f"Provider：{analysis.ai_insight.provider}")
        print(f"Model：{analysis.ai_insight.model}")


if __name__ == "__main__":
    main()
