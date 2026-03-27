"""tests/conftest.py - 测试 fixtures：利用 pytest-playwright 内置 fixtures"""
import logging

import pytest
from playwright.sync_api import sync_playwright

from utils.config_loader import load_config
from pages.login_page import LoginPage
from pages.service_select_page import ServiceSelectPage
from pages.home_page import HomePage

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def config():
    """加载测试配置（session 作用域，只加载一次）"""
    return load_config()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright, config):
    """
    覆盖 pytest-playwright 的 browser_context_args fixture，
    注入 iPhone XR 设备模拟参数。
    """
    device_name = config.get("device_name", "iPhone XR")
    device = playwright.devices[device_name]

    return {
        **browser_context_args,
        **device,
        "ignore_https_errors": True,
        "locale": "zh-CN",
    }


@pytest.fixture(scope="session")
def _session_page(browser, browser_context_args, config):
    """
    session 作用域的 page，整个测试会话只创建一次。
    不使用 pytest-playwright 默认的 function 级 page fixture。
    """
    context = browser.new_context(**browser_context_args)
    context.set_default_timeout(config.get("timeout", 15000))
    p = context.new_page()

    yield p

    p.close()
    context.close()


@pytest.fixture(scope="session")
def logged_in_page(_session_page, config):
    """
    session 作用域：完成登录 + 服务/账套/产品选择。
    整个测试会话只登录一次，所有用例共享同一个已登录的 page。
    """
    page = _session_page
    page.set_default_timeout(config.get("timeout", 15000))

    # 登录
    login_page = LoginPage(page, config)
    login_page.login()

    # 选择服务/账套/产品
    service_page = ServiceSelectPage(page, config)
    service_page.complete_selection()

    # 进入首页后点击全部应用，进入应用列表页
    home_page = HomePage(page, config)
    home_page.wait_for_home_loaded()
    home_page.click_all_apps()

    logger.info("登录及服务选择完成，已进入全部应用页面")
    yield page


@pytest.fixture(autouse=True)
def reset_to_all_apps(logged_in_page, config):
    """每个测试用例执行前，确保页面在全部应用页。
    如果已在 allApp 页则跳过，避免不必要的导航。
    """
    page = logged_in_page
    if "/setting/allApp/index" in page.url:
        yield
        return

    logger.info(f"页面不在全部应用页 ({page.url})，重置中...")
    # 从当前URL提取 base（去掉hash和缓存参数），导航回首页
    base = page.url.split('#')[0].split('&_r=')[0]
    page.goto(base, wait_until="networkidle")
    page.wait_for_timeout(2000)

    # 点击全部应用
    home_page = HomePage(page, config)
    home_page.click_all_apps()
    page.wait_for_timeout(1000)
    logger.info(f"已重置到全部应用页: {page.url}")
    yield
