import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT_DIR / "examples"
OUTPUTS_DIR = ROOT_DIR / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"
TESTS_DIR = OUTPUTS_DIR / "tests"

CODE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
}


def ensure_output_dirs() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    TESTS_DIR.mkdir(parents=True, exist_ok=True)


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default)

