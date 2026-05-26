from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class LogSignal:
    severity: str
    source: str
    message: str
    line_no: int
    category: str = "unknown"


@dataclass
class ScreenshotSummary:
    path: Optional[Path]
    width: int = 0
    height: int = 0
    visual_hints: List[str] = field(default_factory=list)
    vision_status: str = "not_configured"
    vision_provider: str = ""
    vision_model: str = ""
    vision_caption: str = ""


@dataclass
class CodeSnippet:
    path: Path
    start_line: int
    end_line: int
    language: str
    text: str


@dataclass
class CodeHit:
    path: Path
    start_line: int
    end_line: int
    score: int
    reason: str
    preview: str


@dataclass
class UploadedCase:
    name: str
    description: str
    screenshot_path: Optional[Path] = None
    video_path: Optional[Path] = None
    frontend_log: str = ""
    backend_log: str = ""
    code_root: Optional[Path] = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class AIInsight:
    provider: str
    model: str
    enabled: bool
    status: str
    content: str = ""


@dataclass
class BugAnalysis:
    title: str
    bug_type: str
    severity: str
    affected_module: str
    summary: str
    evidence: List[str]
    reproduce_steps: List[str]
    root_cause: str
    suspicious_locations: List[CodeHit]
    fix_suggestions: List[str]
    tests: Dict[str, str]
    analysis_mode: str = "rules"
    confidence: float = 0.72
    ai_insight: Optional[AIInsight] = None
