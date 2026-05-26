import json
import tempfile
import zipfile
from pathlib import Path

import streamlit as st

from src.bug_reasoner import analyze_case
from src.config import EXAMPLES_DIR, OUTPUTS_DIR
from src.models import UploadedCase
from src.report_generator import render_markdown, save_outputs
from src.video_analyzer import extract_keyframes


st.set_page_config(page_title="MultiBug-Agent", layout="wide")


def list_examples():
    return sorted(path for path in EXAMPLES_DIR.glob("case_*") if path.is_dir())


def load_example(case_dir: Path) -> UploadedCase:
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


def save_upload(uploaded, target: Path):
    if not uploaded:
        return None
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(uploaded.getbuffer())
    return target


def safe_extract_zip(zip_path: Path, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            member_path = (target_dir / member.filename).resolve()
            if not str(member_path).startswith(str(target_dir.resolve())):
                raise ValueError(f"Unsafe zip path: {member.filename}")
        zf.extractall(target_dir)
    return target_dir


st.title("MultiBug-Agent")
st.caption("多模态 UI 缺陷定位与自动化测试用例生成平台")

with st.sidebar:
    mode = st.radio("输入方式", ["示例场景", "手动上传"])
    use_llm = st.toggle("AI 二次审查", value=False, help="需要配置 DEEPSEEK_API_KEY 或 LLM_API_KEY")
    st.divider()
    st.write("输出内容")
    st.checkbox("Bug 报告", value=True, disabled=True)
    st.checkbox("pytest 测试", value=True, disabled=True)
    st.checkbox("Playwright 测试", value=True, disabled=True)

left, right = st.columns([0.42, 0.58])

case = None
with left:
    st.subheader("输入")
    if mode == "示例场景":
        examples = list_examples()
        labels = [path.name for path in examples]
        selected = st.selectbox("选择一个 Bug 场景", labels)
        case = load_example(examples[labels.index(selected)])
        st.image(str(case.screenshot_path), caption="页面截图", use_container_width=True)
        if case.video_path:
            if case.video_path.suffix.lower() == ".gif":
                st.image(str(case.video_path), caption="操作录屏", use_container_width=True)
            else:
                st.video(str(case.video_path))
        with st.expander("用户描述", expanded=True):
            st.write(case.description)
        with st.expander("前端日志"):
            st.code(case.frontend_log, language="text")
        with st.expander("后端日志"):
            st.code(case.backend_log, language="text")
    else:
        description = st.text_area("用户描述", height=120, placeholder="例如：点击注册后页面报错，控制台出现 TypeError...")
        screenshot = st.file_uploader("页面截图", type=["png", "jpg", "jpeg"])
        video = st.file_uploader("操作录屏", type=["mp4", "gif", "mov"])
        frontend_log = st.text_area("前端 console 日志", height=140)
        backend_log = st.text_area("后端日志", height=140)
        code_zip = st.file_uploader("代码 zip", type=["zip"])
        temp_dir = Path(tempfile.mkdtemp(prefix="multibug_upload_"))
        screenshot_path = save_upload(screenshot, temp_dir / "screenshot.png")
        video_path = save_upload(video, temp_dir / f"operation{Path(video.name).suffix}") if video else None
        code_root = None
        if code_zip:
            zip_path = save_upload(code_zip, temp_dir / "code.zip")
            code_root = safe_extract_zip(zip_path, temp_dir / "code")
        case = UploadedCase(
            name="manual_upload",
            description=description,
            screenshot_path=screenshot_path,
            video_path=video_path,
            frontend_log=frontend_log,
            backend_log=backend_log,
            code_root=code_root,
            metadata={},
        )

analyze = st.button("开始分析", type="primary", use_container_width=True)

with right:
    st.subheader("分析结果")
    if analyze:
        if not case or not case.description.strip():
            st.warning("请至少填写用户描述。")
        else:
            with st.spinner("正在分析截图、日志和代码..."):
                analysis = analyze_case(case, use_llm=use_llm)
                report = render_markdown(analysis)
                report_path = save_outputs(case.name, analysis)
                keyframes = extract_keyframes(case.video_path, OUTPUTS_DIR / "keyframes" / case.name) if case.video_path else []

            st.success(f"分析完成，报告已保存：{report_path}")
            st.markdown(report)
            if keyframes:
                st.write("录屏关键帧")
                st.image([str(path) for path in keyframes], width=220)
            st.download_button("下载 Bug 报告", data=report, file_name=f"{case.name}_bug_report.md", mime="text/markdown")
            st.download_button("下载 pytest 测试", data=analysis.tests["pytest"], file_name=f"{case.name}_pytest_test.py")
            st.download_button("下载 Playwright 测试", data=analysis.tests["playwright"], file_name=f"{case.name}_playwright_test.py")
    else:
        st.info("选择左侧示例或上传材料后，点击“开始分析”。")
