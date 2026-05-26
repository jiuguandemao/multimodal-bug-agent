from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def font(size=22, bold=False):
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "arial.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


F_TITLE = font(28, True)
F_H2 = font(22, True)
F_BODY = font(18)
F_SMALL = font(15)
F_MONO = font(14)


def draw_base(title, subtitle="Demo Web App"):
    img = Image.new("RGB", (1280, 760), "#f5f7fb")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1280, 64], fill="#18202f")
    d.text((28, 18), subtitle, font=F_H2, fill="#ffffff")
    d.rounded_rectangle([24, 92, 1256, 724], radius=8, fill="#ffffff", outline="#d9dee9")
    d.text((58, 124), title, font=F_TITLE, fill="#172033")
    return img, d


def button(d, xy, text, fill="#2563eb"):
    x1, y1, x2, y2 = xy
    d.rounded_rectangle(xy, radius=6, fill=fill)
    d.text((x1 + 22, y1 + 10), text, font=F_BODY, fill="#ffffff")


def input_box(d, xy, label, value="", error=None):
    x1, y1, x2, y2 = xy
    d.text((x1, y1 - 28), label, font=F_SMALL, fill="#46546b")
    d.rounded_rectangle(xy, radius=6, fill="#ffffff", outline="#cbd5e1", width=2)
    if value:
        d.text((x1 + 14, y1 + 12), value, font=F_BODY, fill="#172033")
    if error:
        d.text((x1, y2 + 8), error, font=F_SMALL, fill="#dc2626")


def toast(d, text, kind="error"):
    fill = "#fef2f2" if kind == "error" else "#eff6ff"
    outline = "#ef4444" if kind == "error" else "#3b82f6"
    d.rounded_rectangle([820, 108, 1228, 176], radius=8, fill=fill, outline=outline, width=2)
    d.text((846, 130), text, font=F_BODY, fill="#991b1b" if kind == "error" else "#1d4ed8")


def save_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def save_json(path, data):
    import json

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def case_register_500():
    case = EXAMPLES / "case_01_register_500"
    case.mkdir(parents=True, exist_ok=True)
    img, d = draw_base("用户注册")
    input_box(d, [98, 210, 560, 260], "用户名", "demo_user")
    input_box(d, [98, 310, 560, 360], "密码", "123456")
    button(d, [98, 410, 250, 460], "提交注册")
    toast(d, "注册失败：服务器异常 500")
    d.rectangle([92, 520, 1180, 666], fill="#0f172a")
    d.text((116, 544), "Console", font=F_SMALL, fill="#93c5fd")
    d.text((116, 574), "POST /api/register 500 (Internal Server Error)", font=F_MONO, fill="#fecaca")
    d.text((116, 604), "TypeError: Cannot read properties of undefined (reading 'user')", font=F_MONO, fill="#fecaca")
    img.save(case / "screenshot.png")
    save_text(case / "description.txt", "点击注册按钮后页面提示服务器异常，用户无法完成注册。")
    save_text(
        case / "frontend.log",
        """
[ERROR] Register.jsx:48 POST /api/register 500 (Internal Server Error)
[ERROR] TypeError: Cannot read properties of undefined (reading 'user') at handleSubmit Register.jsx:48
""",
    )
    save_text(
        case / "backend.log",
        """
ERROR register_service.py:37 Traceback (most recent call last)
ERROR /api/register 500 ValueError: birthday must not be empty
""",
    )
    save_json(
        case / "metadata.json",
        {
            "name": "注册提交返回 500",
            "category": "server_error",
            "module": "用户注册模块",
            "screen_state": "注册表单提交后出现服务端 500 错误提示",
            "ui_hint": "页面右上角出现红色错误 Toast",
            "reproduce_steps": "打开注册页面|输入用户名和密码|点击提交注册|页面提示服务器异常 500",
        },
    )
    write_register_code(case / "code")


def write_register_code(root):
    save_text(
        root / "frontend" / "Register.jsx",
        """
export async function handleSubmit(form) {
  const response = await fetch("/api/register", {
    method: "POST",
    body: JSON.stringify(form)
  });
  const data = await response.json();
  setCurrentUser(data.user.name);
}
""",
    )
    save_text(
        root / "backend" / "register_service.py",
        """
def register_user(payload):
    username = payload.get("username")
    password = payload.get("password")
    birthday = payload["birthday"]
    if not username or not password:
        raise ValueError("username and password required")
    return {"id": 1, "username": username, "birthday": birthday}
""",
    )


def case_login_timeout():
    case = EXAMPLES / "case_02_login_timeout"
    case.mkdir(parents=True, exist_ok=True)
    frames = []
    for step in range(28):
        img, d = draw_base("登录")
        input_box(d, [100, 214, 560, 264], "账号", "demo")
        input_box(d, [100, 314, 560, 364], "密码", "******")
        button(d, [100, 414, 230, 464], "登录")
        d.rounded_rectangle([760, 220, 1130, 510], radius=8, fill="#f8fafc", outline="#dbe3ef")
        d.text((800, 254), "登录状态", font=F_H2, fill="#172033")
        if step < 8:
            d.text((800, 310), "等待用户点击登录", font=F_BODY, fill="#475569")
        else:
            d.ellipse([810, 332, 850, 372], outline="#2563eb", width=5)
            d.arc([810, 332, 850, 372], start=step * 20, end=step * 20 + 90, fill="#ffffff", width=6)
            d.text((870, 340), "登录中，请稍候...", font=F_BODY, fill="#2563eb")
            d.text((800, 404), "Loading 已持续 12s 未结束", font=F_SMALL, fill="#dc2626")
        frames.append(img)
    frames[-1].save(case / "screenshot.png")
    save_video(case / "operation.mp4", frames)
    save_text(case / "description.txt", "输入账号密码后点击登录，按钮进入 loading 状态后一直不恢复。")
    save_text(
        case / "frontend.log",
        """
[WARN] Login.jsx:31 request /api/login exceeded 8000ms
[ERROR] AxiosError: timeout of 8000ms exceeded at submit Login.jsx:31
""",
    )
    save_text(
        case / "backend.log",
        """
WARN /api/login slow query cost=12842ms user=demo
WARN auth_service.py:62 retry password provider timeout
""",
    )
    save_json(
        case / "metadata.json",
        {
            "name": "登录 Loading 卡死",
            "category": "timeout",
            "module": "登录认证模块",
            "screen_state": "登录按钮点击后持续 loading",
            "ui_hint": "页面未展示超时错误，也未释放 loading 状态",
            "reproduce_steps": "打开登录页|输入账号密码|点击登录|页面一直显示登录中",
        },
    )
    save_text(
        case / "code" / "frontend" / "Login.jsx",
        """
export async function submitLogin(form) {
  setLoading(true);
  const response = await api.post("/api/login", form, { timeout: 8000 });
  setToken(response.data.token);
  setLoading(false);
}
""",
    )
    save_text(
        case / "code" / "backend" / "auth_service.py",
        """
def login(username, password):
    user = query_user(username)
    token = password_provider.verify(username, password)
    return {"token": token, "user": user}
""",
    )


def case_upload_failed():
    case = EXAMPLES / "case_03_upload_failed"
    case.mkdir(parents=True, exist_ok=True)
    img, d = draw_base("图片上传")
    d.rounded_rectangle([96, 214, 650, 468], radius=8, fill="#f8fafc", outline="#cbd5e1", width=2)
    d.text((138, 258), "拖拽图片到这里，或点击选择文件", font=F_BODY, fill="#475569")
    d.text((138, 314), "selected: product-banner-8mb.png", font=F_SMALL, fill="#64748b")
    d.rectangle([138, 366, 560, 386], fill="#e2e8f0")
    d.rectangle([138, 366, 412, 386], fill="#ef4444")
    d.text((138, 408), "上传失败：文件超过限制", font=F_BODY, fill="#dc2626")
    toast(d, "413 Payload Too Large")
    img.save(case / "screenshot.png")
    save_text(case / "description.txt", "上传 8MB 图片时失败，页面只显示上传失败，没有告诉用户限制是多少。")
    save_text(case / "frontend.log", "[ERROR] Upload.jsx:52 POST /api/upload 413 Payload Too Large")
    save_text(case / "backend.log", "ERROR upload_controller.py:29 file too large, max_size=5MB, actual=8.1MB")
    save_json(
        case / "metadata.json",
        {
            "name": "图片上传超过限制",
            "category": "upload_limit",
            "module": "文件上传模块",
            "screen_state": "上传进度条变红并提示失败",
            "ui_hint": "错误提示没有说明最大文件大小",
        },
    )
    save_text(
        case / "code" / "backend" / "upload_controller.py",
        """
MAX_SIZE = 5 * 1024 * 1024

def upload(file):
    if file.size > MAX_SIZE:
        return {"message": "upload failed"}, 413
    return save_file(file)
""",
    )
    save_text(
        case / "code" / "frontend" / "Upload.jsx",
        """
export async function uploadFile(file) {
  const response = await api.post("/api/upload", file);
  if (!response.ok) {
    setError("上传失败");
  }
}
""",
    )


def case_blank_page():
    case = EXAMPLES / "case_04_blank_page_typeerror"
    case.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (1280, 760), "#ffffff")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1280, 64], fill="#18202f")
    d.text((28, 18), "Demo Web App", font=F_H2, fill="#ffffff")
    d.text((520, 330), "页面空白", font=F_TITLE, fill="#cbd5e1")
    d.rectangle([90, 560, 1190, 682], fill="#0f172a")
    d.text((116, 586), "Console", font=F_SMALL, fill="#93c5fd")
    d.text((116, 616), "TypeError: Cannot read properties of null (reading 'avatar')", font=F_MONO, fill="#fecaca")
    img.save(case / "screenshot.png")
    save_text(case / "description.txt", "进入个人中心后页面白屏，刷新也无法恢复。")
    save_text(case / "frontend.log", "[ERROR] Profile.jsx:27 TypeError: Cannot read properties of null (reading 'avatar')")
    save_text(case / "backend.log", "INFO /api/profile 200 user=null")
    save_json(
        case / "metadata.json",
        {
            "name": "个人中心页面白屏",
            "category": "frontend_type_error",
            "module": "个人中心模块",
            "screen_state": "页面主体几乎空白",
            "ui_hint": "控制台显示读取 null.avatar 失败",
        },
    )
    save_text(
        case / "code" / "frontend" / "Profile.jsx",
        """
export function Profile({ user }) {
  return (
    <section>
      <img src={user.avatar} />
      <h1>{user.name}</h1>
    </section>
  );
}
""",
    )


def case_order_amount():
    case = EXAMPLES / "case_05_order_amount_error"
    case.mkdir(parents=True, exist_ok=True)
    img, d = draw_base("订单详情")
    d.text((98, 210), "商品", font=F_H2, fill="#172033")
    rows = [("键盘", "1", "¥89.90"), ("运费", "1", "¥10.00"), ("优惠", "1", "-¥5.00")]
    y = 260
    for name, qty, price in rows:
        d.text((110, y), name, font=F_BODY, fill="#172033")
        d.text((480, y), qty, font=F_BODY, fill="#475569")
        d.text((760, y), price, font=F_BODY, fill="#172033")
        y += 56
    d.line([96, 430, 980, 430], fill="#dbe3ef", width=2)
    d.text((110, 470), "页面展示总额", font=F_H2, fill="#172033")
    d.text((760, 470), "¥99.90", font=F_TITLE, fill="#dc2626")
    d.text((110, 528), "接口返回应为 ¥94.90", font=F_BODY, fill="#64748b")
    toast(d, "金额与接口返回不一致")
    img.save(case / "screenshot.png")
    save_text(case / "description.txt", "订单详情页面展示总金额和接口返回金额不一致。")
    save_text(case / "frontend.log", "[WARN] OrderDetail.tsx:88 amount mismatch uiTotal=99.90 apiTotal=94.90")
    save_text(case / "backend.log", "INFO /api/orders/1001 total=94.90 items=89.90 freight=10.00 discount=5.00")
    save_json(
        case / "metadata.json",
        {
            "name": "订单金额显示错误",
            "category": "data_mismatch",
            "module": "订单结算模块",
            "screen_state": "页面展示总额与接口返回金额不一致",
            "ui_hint": "折扣没有被正确扣减",
        },
    )
    save_text(
        case / "code" / "frontend" / "OrderDetail.tsx",
        """
export function calcTotal(order) {
  const items = order.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  return Number((items + order.freight).toFixed(2));
}
""",
    )


def case_permission():
    case = EXAMPLES / "case_06_permission_403"
    case.mkdir(parents=True, exist_ok=True)
    img, d = draw_base("用户管理")
    d.rounded_rectangle([120, 230, 640, 430], radius=8, fill="#fff7ed", outline="#fb923c", width=2)
    d.text((160, 274), "访问受限", font=F_TITLE, fill="#c2410c")
    d.text((160, 334), "当前账号无权查看用户管理列表", font=F_BODY, fill="#9a3412")
    toast(d, "GET /api/admin/users 403 Forbidden")
    img.save(case / "screenshot.png")
    save_text(case / "description.txt", "普通用户访问用户管理页面时接口返回 403，但页面没有跳转到统一无权限页。")
    save_text(case / "frontend.log", "[ERROR] AdminUsers.jsx:19 GET /api/admin/users 403 Forbidden")
    save_text(case / "backend.log", "WARN permission.py:44 user_role=viewer denied permission=admin.users.read")
    save_json(
        case / "metadata.json",
        {
            "name": "用户管理权限不足",
            "category": "permission",
            "module": "权限管理模块",
            "screen_state": "页面局部显示访问受限",
            "ui_hint": "接口返回 403 Forbidden",
        },
    )
    save_text(
        case / "code" / "backend" / "permission.py",
        """
def require_permission(user, permission):
    if permission not in user.permissions:
        return False
    return True
""",
    )
    save_text(
        case / "code" / "frontend" / "AdminUsers.jsx",
        """
export async function loadUsers() {
  const response = await api.get("/api/admin/users");
  setUsers(response.data);
}
""",
    )


def save_video(path, frames):
    try:
        import imageio.v2 as imageio

        imageio.mimsave(path, frames, fps=8, quality=7)
    except Exception:
        gif_path = path.with_suffix(".gif")
        frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=125, loop=0)


def main():
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    case_register_500()
    case_login_timeout()
    case_upload_failed()
    case_blank_page()
    case_order_amount()
    case_permission()
    (ROOT / "outputs").mkdir(exist_ok=True)
    print(f"Demo assets generated under: {EXAMPLES}")


if __name__ == "__main__":
    main()

