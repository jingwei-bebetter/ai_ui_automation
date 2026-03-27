import logging
from typing import List

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class AppListPage(BasePage):
    """全部应用 - 分类应用列表页面对象"""

    # 应用名称选择器：.all-app-content 容器内的 taro-text-core.text
    APP_NAME_SELECTOR = '.all-app-content taro-text-core.text'

    def __init__(self, page: Page, config: dict):
        super().__init__(page, config)

    @allure.step("点击分类: {category_name}")
    def click_category(self, category_name: str):
        """点击指定的应用分类（如 销售管理）"""
        category_locator = self.page.locator(
            f'taro-view-core.vertical-menu__wrapper__content:has-text("{category_name}")'
        )
        if category_locator.count() > 0:
            self.click(category_locator.first)
        else:
            self.click(self.page.get_by_text(category_name, exact=True).first)
        self.page.wait_for_timeout(1000)

    @allure.step("获取当前分类下所有应用名称")
    def get_app_names(self, category_name: str) -> List[str]:
        """获取指定分类下所有应用名称"""
        app_names = []

        try:
            app_items = self.page.locator(self.APP_NAME_SELECTOR)
            count = app_items.count()
            if count > 0:
                app_names = self.get_texts(app_items)
        except Exception as e:
            logger.warning(f"获取应用名称失败: {e}")
            self.screenshot("get_app_names_failed")

        logger.info(f"分类 [{category_name}] 下获取到 {len(app_names)} 个应用: {app_names}")
        allure.attach(
            str(app_names),
            name=f"{category_name}_应用列表",
            attachment_type=allure.attachment_type.TEXT,
        )
        return app_names
