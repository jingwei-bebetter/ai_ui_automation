"""根 conftest.py - pytest 插件注册、截图钩子"""
import base64
import os
import logging

import allure
import pytest
from pytest_html import extras as html_extras

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动截图，附加到 pytest-html 和 allure 报告"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # 尝试从 fixture 获取 page 对象
        page = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
        if page:
            project_root = os.path.dirname(os.path.abspath(__file__))
            screenshot_dir = os.path.join(project_root, "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)

            screenshot_name = f"{item.nodeid.replace('::', '_').replace('/', '_')}"
            screenshot_path = os.path.join(screenshot_dir, f"{screenshot_name}.png")

            try:
                page.screenshot(path=screenshot_path)

                # 附加到 allure 报告
                allure.attach.file(
                    screenshot_path,
                    name="失败截图",
                    attachment_type=allure.attachment_type.PNG,
                )

                # 附加到 pytest-html 报告（base64 内嵌，配合 --self-contained-html）
                with open(screenshot_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                report.extras = getattr(report, "extras", [])
                report.extras.append(html_extras.image(b64, mime_type="image/png"))
            except Exception as e:
                logging.getLogger(__name__).warning(f"截图失败: {e}")
