from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def font(size=24, bold=False):
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def architecture_png():
    ASSETS.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (1600, 920), "#f7f9fc")
    d = ImageDraw.Draw(img)
    title = font(44, True)
    h = font(25, True)
    body = font(19)
    d.text((60, 42), "MultiBug-Agent Architecture", font=title, fill="#0f172a")

    boxes = [
        ("Multimodal Inputs", "Screenshot\nVideo keyframes\nFrontend logs\nBackend logs\nCode zip\nUser description", 70, 160, "#dbeafe"),
        ("Evidence Extraction", "VLM caption\nLog parsing\nCode splitting\nKeyword retrieval\nFrame sampling", 430, 160, "#dcfce7"),
        ("Reasoning Layer", "Rule engine\nSuspicious code ranking\nDeepSeek review\nConfidence scoring", 790, 160, "#fef3c7"),
        ("Outputs", "Bug report\nRoot cause\nFix suggestions\npytest tests\nPlaywright tests", 1150, 160, "#fee2e2"),
    ]
    for title_text, content, x, y, fill in boxes:
        d.rounded_rectangle([x, y, x + 300, y + 520], radius=16, fill=fill, outline="#94a3b8", width=2)
        d.text((x + 24, y + 26), title_text, font=h, fill="#0f172a")
        d.multiline_text((x + 24, y + 92), content, font=body, fill="#334155", spacing=18)
    for x in (374, 734, 1094):
        d.line([x, 420, x + 48, 420], fill="#2563eb", width=5)
        d.polygon([(x + 48, 420), (x + 30, 408), (x + 30, 432)], fill="#2563eb")
    d.text((70, 740), "Design principle: deterministic evidence extraction first, LLM/VLM as optional enhancement.", font=font(24, True), fill="#1e3a8a")
    d.text((70, 790), "The project remains runnable without API keys, and becomes stronger when DeepSeek/Qwen-VL keys are configured.", font=font(21), fill="#334155")
    img.save(ASSETS / "architecture.png")


def demo_gif():
    ASSETS.mkdir(parents=True, exist_ok=True)
    frames = []
    captions = [
        ("1. Select a reproducible bug scenario", "Register submit returns 500 with console and backend evidence."),
        ("2. Analyze multimodal evidence", "Screenshot, logs, code snippets and user description are fused."),
        ("3. Locate suspicious code", "Ranking points to backend validation and frontend null handling."),
        ("4. Generate report and tests", "Bug report, pytest and Playwright templates are exported."),
        ("5. Optional AI review", "DeepSeek and Qwen-VL can enhance reasoning when API keys are configured."),
    ]
    for idx, (main, sub) in enumerate(captions):
        img = Image.new("RGB", (1280, 720), "#f8fafc")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 1280, 76], fill="#111827")
        d.text((36, 22), "MultiBug-Agent Demo", font=font(28, True), fill="#ffffff")
        d.rounded_rectangle([56, 128, 1224, 620], radius=14, fill="#ffffff", outline="#cbd5e1", width=2)
        d.text((96, 176), main, font=font(36, True), fill="#0f172a")
        d.text((96, 240), sub, font=font(24), fill="#475569")
        d.rounded_rectangle([96, 330, 1184, 500], radius=10, fill="#eff6ff", outline="#93c5fd", width=2)
        d.text((132, 370), "Evidence -> Reasoning -> Report -> Tests", font=font(30, True), fill="#1d4ed8")
        d.text((132, 430), f"Step {idx + 1}/5", font=font(24), fill="#334155")
        frames.append(img)
    frames[0].save(ASSETS / "demo.gif", save_all=True, append_images=frames[1:], duration=1100, loop=0)


def main():
    architecture_png()
    demo_gif()
    print(f"Assets written to {ASSETS}")


if __name__ == "__main__":
    main()
