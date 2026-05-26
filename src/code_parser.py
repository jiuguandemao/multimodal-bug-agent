import re
from pathlib import Path
from typing import Iterable, List, Optional

from .config import CODE_EXTENSIONS
from .models import CodeSnippet


def collect_code_snippets(code_root: Optional[Path], max_chars: int = 1800) -> List[CodeSnippet]:
    if not code_root or not code_root.exists():
        return []
    snippets: List[CodeSnippet] = []
    for path in _iter_code_files(code_root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="gbk", errors="ignore")
        language = CODE_EXTENSIONS.get(path.suffix.lower(), "text")
        display_path = Path("code") / path.relative_to(code_root)
        snippets.extend(_split_file(display_path, text, language, max_chars=max_chars))
    return snippets


def _iter_code_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in CODE_EXTENSIONS:
            if any(part in {"node_modules", ".venv", "venv", "__pycache__"} for part in path.parts):
                continue
            yield path


def _split_file(path: Path, text: str, language: str, max_chars: int) -> List[CodeSnippet]:
    lines = text.splitlines()
    if not lines:
        return []

    start_candidates = [1]
    pattern = re.compile(r"^\s*(def |class |function |const |let |export |async function |public |private |protected )")
    for idx, line in enumerate(lines, start=1):
        if idx > 1 and pattern.search(line):
            start_candidates.append(idx)
    start_candidates.append(len(lines) + 1)

    snippets: List[CodeSnippet] = []
    for pos in range(len(start_candidates) - 1):
        start = start_candidates[pos]
        end = start_candidates[pos + 1] - 1
        block = "\n".join(lines[start - 1:end])
        if len(block) <= max_chars:
            snippets.append(CodeSnippet(path=path, start_line=start, end_line=end, language=language, text=block))
            continue
        chunk_start = start
        chunk: List[str] = []
        size = 0
        for line_no in range(start, end + 1):
            line = lines[line_no - 1]
            if size + len(line) > max_chars and chunk:
                snippets.append(
                    CodeSnippet(
                        path=path,
                        start_line=chunk_start,
                        end_line=line_no - 1,
                        language=language,
                        text="\n".join(chunk),
                    )
                )
                chunk_start = line_no
                chunk = []
                size = 0
            chunk.append(line)
            size += len(line) + 1
        if chunk:
            snippets.append(CodeSnippet(path=path, start_line=chunk_start, end_line=end, language=language, text="\n".join(chunk)))
    return snippets
