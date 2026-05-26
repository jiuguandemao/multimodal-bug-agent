from pathlib import Path

from src.bug_reasoner import analyze_case
from src.models import UploadedCase


def test_register_case_generates_report():
    root = Path(__file__).resolve().parents[1] / "examples" / "case_01_register_500"
    case = UploadedCase(
        name="register submit returns 500",
        description=(root / "description.txt").read_text(encoding="utf-8"),
        screenshot_path=root / "screenshot.png",
        frontend_log=(root / "frontend.log").read_text(encoding="utf-8"),
        backend_log=(root / "backend.log").read_text(encoding="utf-8"),
        code_root=root / "code",
        metadata={"category": "server_error", "module": "user registration"},
    )

    analysis = analyze_case(case)

    assert "500" in analysis.bug_type
    assert analysis.suspicious_locations
    assert analysis.suspicious_locations[0].path.as_posix().endswith("register_service.py")
    assert "pytest" in analysis.tests
    assert "playwright" in analysis.tests
