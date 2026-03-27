import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class HomePage(BasePage):
    """首页页面对象"""

    # 定位器 - 根据实际页面结构可能需要调整
    ALL_APPS_BUTTON = 'text=全部应用'

    def __init__(self, page: Page, config: dict):
        super().__init__(page, config)

    @allure.step("等待首页加载完成")
    def wait_for_home_loaded(self):
        """等待首页加载完成"""
        self.page.wait_for_load_state("networkidle", timeout=self.timeout)

    @allure.step("点击全部应用")
    def click_all_apps(self):
        """点击全部应用入口"""
        self.click(self.ALL_APPS_BUTTON)
        self.page.wait_for_load_state("networkidle", timeout=self.timeout)
