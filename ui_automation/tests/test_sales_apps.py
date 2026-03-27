"""测试用例：验证全部应用各分类下的应用名称"""
import logging

import allure
import pytest

from pages.app_list_page import AppListPage

logger = logging.getLogger(__name__)


@allure.feature("全部应用")
class TestAllAppsCategories:
    """全部应用 - 各分类应用列表验证（共享登录状态，不重复登录）"""

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("category", [
        "销售管理",
        "采购管理",
        "仓库管理",
        "车销",
        "访销",
    ])
    def test_category_contains_expected_apps(self, logged_in_page, config, category):
        """
        验证指定分类下包含所有期望的应用。

        测试步骤：
        1. 在全部应用页面，点击左侧分类
        2. 获取该分类下所有应用名称
        3. 断言期望的应用名称都包含在实际列表中
        """
        allure.dynamic.story(f"{category}应用列表验证")
        allure.dynamic.title(f"验证【{category}】下包含所有期望的应用")

        page = logged_in_page

        # 1. 点击分类
        app_list_page = AppListPage(page, config)
        app_list_page.click_category(category)

        # 2. 获取所有应用名称
        actual_apps = app_list_page.get_app_names(category)
        logger.info(f"[{category}] 实际获取到的应用列表: {actual_apps}")

        # 3. 断言
        expected_apps = config.get("expected_apps", {}).get(category, [])
        assert len(actual_apps) > 0, f"【{category}】下未获取到任何应用名称"

        if expected_apps:
            missing_apps = set(expected_apps) - set(actual_apps)
            assert not missing_apps, (
                f"以下期望的应用未在【{category}】中找到: {missing_apps}\n"
                f"实际应用列表: {actual_apps}"
            )
            logger.info(f"[{category}] 断言通过: 所有期望应用均包含在实际列表中")
        else:
            logger.warning(
                f"未配置【{category}】的期望应用列表，实际获取到: {actual_apps}"
            )
