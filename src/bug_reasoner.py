from typing import Dict, List

from .code_locator import locate_suspicious_code
from .code_parser import collect_code_snippets
from .llm_client import try_llm_enhance
from .log_parser import dominant_category, extract_keywords, parse_logs, summarize_signals
from .models import AIInsight, BugAnalysis, ScreenshotSummary, UploadedCase
from .multimodal_context import build_llm_prompt, build_multimodal_context
from .screenshot_analyzer import analyze_screenshot
from .test_generator import generate_tests
from .vision_analyzer import enhance_screenshot_with_vision


CATEGORY_MAP = {
    "server_error": "接口异常 / 服务端 500",
    "frontend_type_error": "前端空值异常 / 页面白屏",
    "timeout": "接口超时 / Loading 卡死",
    "permission": "权限校验异常",
    "upload_limit": "上传限制异常",
    "data_mismatch": "金额计算不一致",
    "network": "网络请求异常",
    "unknown": "待进一步确认",
}


def analyze_case(case: UploadedCase, use_llm: bool = False) -> BugAnalysis:
    signals = parse_logs(case.frontend_log, case.backend_log)
    category = case.metadata.get("category") or dominant_category(signals)
    screenshot = analyze_screenshot(case.screenshot_path, case.metadata)
    screenshot = enhance_screenshot_with_vision(screenshot)
    snippets = collect_code_snippets(case.code_root)
    keywords = extract_keywords(case.description, signals)
    if case.metadata.get("module"):
        keywords.append(case.metadata["module"].lower())
    suspicious = locate_suspicious_code(snippets, keywords, signals)

    bug_type = CATEGORY_MAP.get(category, CATEGORY_MAP["unknown"])
    analysis = BugAnalysis(
        title=_title(case.name, bug_type),
        bug_type=bug_type,
        severity=_severity(category, signals),
        affected_module=_module(case, category),
        summary=_summary(case, bug_type, screenshot),
        evidence=_evidence(case, screenshot, signals),
        reproduce_steps=_steps(case, category),
        root_cause=_root_cause(category, suspicious),
        suspicious_locations=suspicious,
        fix_suggestions=_fix_suggestions(category),
        tests={},
        analysis_mode="rules+retrieval",
        confidence=_confidence(category, signals, suspicious),
    )
    analysis.tests = generate_tests(analysis)
    if use_llm:
        evidence_packet = build_multimodal_context(case, screenshot, signals, suspicious)
        config, status, content = try_llm_enhance(build_llm_prompt(evidence_packet))
        analysis.analysis_mode = "rules+retrieval+llm"
        analysis.ai_insight = AIInsight(
            provider=config.provider,
            model=config.model,
            enabled=True,
            status=status,
            content=content,
        )
    return analysis


def _title(name: str, bug_type: str) -> str:
    return f"{name} - {bug_type}"


def _severity(category: str, signals: List) -> str:
    if category in {"server_error", "frontend_type_error", "timeout"}:
        return "High"
    if category in {"permission", "upload_limit", "data_mismatch"}:
        return "Medium"
    if any(signal.severity == "error" for signal in signals):
        return "Medium"
    return "Low"


def _module(case: UploadedCase, category: str) -> str:
    if case.metadata.get("module"):
        return case.metadata["module"]
    mapping = {
        "server_error": "注册/表单提交模块",
        "frontend_type_error": "页面渲染模块",
        "timeout": "登录认证模块",
        "permission": "权限管理模块",
        "upload_limit": "文件上传模块",
        "data_mismatch": "订单结算模块",
    }
    return mapping.get(category, "未知模块")


def _summary(case: UploadedCase, bug_type: str, screenshot: ScreenshotSummary) -> str:
    hints = "；".join(screenshot.visual_hints[:2])
    return f"用户反馈：{case.description.strip()}。系统判断该问题属于「{bug_type}」。截图线索：{hints}。"


def _evidence(case: UploadedCase, screenshot: ScreenshotSummary, signals: List) -> List[str]:
    evidence = []
    if screenshot.path:
        evidence.append(f"截图尺寸：{screenshot.width}x{screenshot.height}")
    evidence.extend(f"截图线索：{hint}" for hint in screenshot.visual_hints)
    if screenshot.vision_status:
        evidence.append(f"视觉模型状态：{screenshot.vision_status}")
    if screenshot.vision_caption:
        evidence.append(f"视觉模型结论：{screenshot.vision_caption}")
    evidence.extend(summarize_signals(signals))
    if not evidence:
        evidence.append("当前证据不足，建议补充截图、console 日志和接口日志。")
    return evidence


def _steps(case: UploadedCase, category: str) -> List[str]:
    custom = case.metadata.get("reproduce_steps")
    if custom:
        return [step.strip() for step in custom.split("|") if step.strip()]
    defaults: Dict[str, List[str]] = {
        "server_error": ["打开注册页面", "输入用户名和密码", "点击提交", "页面提示服务异常或请求失败"],
        "frontend_type_error": ["打开目标页面", "等待页面加载", "页面出现白屏或内容缺失", "控制台出现 TypeError"],
        "timeout": ["打开登录页面", "输入账号密码", "点击登录", "页面一直处于 loading 状态"],
        "permission": ["使用普通用户登录", "访问管理员页面", "页面或接口返回 403", "缺少清晰的无权限提示"],
        "upload_limit": ["打开上传页面", "选择较大的图片文件", "点击上传", "上传失败且错误提示不明确"],
        "data_mismatch": ["打开订单详情页", "对比商品行金额、运费与总价", "发现页面总金额与接口返回/计算结果不一致"],
    }
    return defaults.get(category, ["打开问题页面", "执行用户描述中的操作", "观察页面异常", "查看日志确认错误"])


def _root_cause(category: str, suspicious) -> str:
    location = suspicious[0].path.as_posix() if suspicious else "暂未定位到具体文件"
    mapping = {
        "server_error": f"后端接口异常处理或参数校验不完整，优先检查 {location}。",
        "frontend_type_error": f"前端对接口返回数据缺少空值保护，渲染阶段触发异常，优先检查 {location}。",
        "timeout": f"接口超时后前端未释放 loading 状态，或后端处理链路耗时过长，优先检查 {location}。",
        "permission": f"权限校验和前端路由提示不一致，优先检查 {location}。",
        "upload_limit": f"上传大小限制与前端提示/后端配置不一致，优先检查 {location}。",
        "data_mismatch": f"金额计算存在前后端口径不一致或精度处理问题，优先检查 {location}。",
    }
    return mapping.get(category, "需要结合更多日志、接口返回和代码上下文继续定位。")


def _fix_suggestions(category: str) -> List[str]:
    mapping = {
        "server_error": ["后端补充参数校验，避免用户输入触发 500", "统一接口错误返回结构", "前端展示明确错误提示", "增加异常分支单元测试"],
        "frontend_type_error": ["对 response.data 等字段增加空值保护", "配置错误边界组件", "接口 mock 覆盖空对象和缺字段场景"],
        "timeout": ["前端请求增加 timeout、重试和 finally 释放 loading", "后端排查慢查询/外部依赖耗时", "增加接口耗时监控"],
        "permission": ["统一后端权限错误码", "前端路由守卫展示无权限页面", "补充普通用户访问管理页面的测试"],
        "upload_limit": ["前后端统一文件大小限制", "前端上传前校验文件大小和类型", "后端返回清晰错误信息"],
        "data_mismatch": ["统一金额计算放在后端或共享函数", "使用 Decimal 避免浮点误差", "增加订单金额快照和边界测试"],
    }
    return mapping.get(category, ["补充日志上下文", "增加复现用例", "定位后补充回归测试"])


def _confidence(category: str, signals: List, suspicious) -> float:
    score = 0.45
    if category != "unknown":
        score += 0.18
    if signals:
        score += min(len(signals), 5) * 0.04
    if suspicious:
        score += min(len(suspicious), 3) * 0.05
    return round(min(score, 0.92), 2)
