from typing import Dict

from .models import BugAnalysis


def generate_tests(analysis: BugAnalysis) -> Dict[str, str]:
    category = analysis.bug_type
    if category == "接口异常 / 服务端 500":
        return _register_500_tests()
    if category == "前端空值异常 / 页面白屏":
        return _blank_page_tests()
    if category == "接口超时 / Loading 卡死":
        return _timeout_tests()
    if category == "权限校验异常":
        return _permission_tests()
    if category == "上传限制异常":
        return _upload_tests()
    if category == "金额计算不一致":
        return _amount_tests()
    return _generic_tests()


def _register_500_tests() -> Dict[str, str]:
    return {
        "pytest": """def test_register_should_validate_required_fields(client):
    response = client.post("/api/register", json={"username": "", "password": "123456"})
    assert response.status_code == 400
    assert "username" in response.get_json()["message"].lower()


def test_register_should_not_return_500_for_duplicate_user(client):
    response = client.post("/api/register", json={"username": "demo", "password": "123456"})
    assert response.status_code in (200, 400, 409)
""",
        "playwright": """def test_register_submit_error_should_show_message(page):
    page.goto("http://localhost:3000/register")
    page.fill("#username", "demo")
    page.fill("#password", "123456")
    page.click("#submit")
    expect(page.locator(".error-message")).to_be_visible()
""",
    }


def _blank_page_tests() -> Dict[str, str]:
    return {
        "pytest": """def test_profile_api_should_return_user_object(client, auth_headers):
    response = client.get("/api/profile", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json().get("user") is not None
""",
        "playwright": """def test_profile_page_should_not_render_blank(page):
    page.goto("http://localhost:3000/profile")
    expect(page.locator("body")).not_to_be_empty()
    expect(page.locator("text=Something went wrong")).not_to_be_visible()
""",
    }


def _timeout_tests() -> Dict[str, str]:
    return {
        "pytest": """def test_login_should_finish_within_timeout(client):
    response = client.post("/api/login", json={"username": "demo", "password": "123456"})
    assert response.status_code in (200, 400, 401)
""",
        "playwright": """def test_login_timeout_should_release_loading_state(page):
    page.goto("http://localhost:3000/login")
    page.fill("#username", "demo")
    page.fill("#password", "123456")
    page.click("#submit")
    expect(page.locator(".loading")).not_to_be_visible(timeout=8000)
    expect(page.locator(".error-message")).to_be_visible()
""",
    }


def _permission_tests() -> Dict[str, str]:
    return {
        "pytest": """def test_admin_api_should_return_403_for_normal_user(client, user_headers):
    response = client.get("/api/admin/users", headers=user_headers)
    assert response.status_code == 403
""",
        "playwright": """def test_forbidden_page_should_show_permission_message(page):
    page.goto("http://localhost:3000/admin/users")
    expect(page.locator("text=无权限")).to_be_visible()
""",
    }


def _upload_tests() -> Dict[str, str]:
    return {
        "pytest": """def test_upload_should_reject_oversized_file(client, auth_headers, large_file):
    response = client.post("/api/upload", headers=auth_headers, data={"file": large_file})
    assert response.status_code == 413
""",
        "playwright": """def test_upload_large_file_should_show_clear_error(page):
    page.goto("http://localhost:3000/upload")
    page.set_input_files("input[type=file]", "tests/fixtures/large-image.png")
    page.click("#upload")
    expect(page.locator(".error-message")).to_contain_text("文件过大")
""",
    }


def _amount_tests() -> Dict[str, str]:
    return {
        "pytest": """def test_order_total_should_equal_items_plus_freight(client):
    response = client.get("/api/orders/1001")
    body = response.get_json()
    expected = sum(item["price"] * item["quantity"] for item in body["items"]) + body["freight"]
    assert round(body["total"], 2) == round(expected, 2)
""",
        "playwright": """def test_order_total_should_match_line_items(page):
    page.goto("http://localhost:3000/orders/1001")
    expect(page.locator("[data-testid=total-amount]")).to_have_text("¥128.80")
""",
    }


def _generic_tests() -> Dict[str, str]:
    return {
        "pytest": """def test_api_should_return_stable_error_contract(client):
    response = client.get("/api/health")
    assert response.status_code < 500
""",
        "playwright": """def test_page_should_show_error_boundary(page):
    page.goto("http://localhost:3000")
    expect(page.locator("body")).not_to_be_empty()
""",
    }

