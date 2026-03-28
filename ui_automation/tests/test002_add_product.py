"""测试用例：新增基础资料 - 商品"""
import logging
import time

import allure
import pytest

from pages.app_list_page import AppListPage
from pages.product_page import ProductPage

logger = logging.getLogger(__name__)


@allure.feature("基础资料")
class TestAddProduct:
    """新增商品资料测试（共享登录状态，不重复登录）"""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("新增商品")
    @allure.title("新增普通商品并验证商品列表可搜索到")
    def test_add_product_and_search(self, logged_in_page, config):
        """
        测试步骤：
        1. 从全部应用进入 仓库管理 → 商品 列表页
        2. 点击右上角⊕进入新增商品页面
        3. 填写必填字段：商品名称、商品类别、计量单位
        4. 点击保存回到商品列表页
        5. 搜索刚新增的商品
        6. 断言商品存在于列表中
        """
        page = logged_in_page

        # 生成唯一商品名称
        product_name = f"普通商品{int(time.time())}"
        category = "自动化新增"
        unit = "g"

        with allure.step("进入仓库管理-商品列表页"):
            app_list = AppListPage(page, config)
            app_list.click_category("仓库管理")

            # 点击"商品"应用
            page.locator(
                '.all-app-content taro-text-core.text:has-text("商品")'
            ).click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)
            logger.info(f"已进入商品列表页: {page.url}")

        product_page = ProductPage(page, config)

        with allure.step(f"新增商品: {product_name}"):
            product_page.add_product(
                product_name=product_name,
                category=category,
                unit=unit,
            )

        with allure.step("验证返回到商品列表页"):
            current_url = page.url
            logger.info(f"保存后当前URL: {current_url}")
            # 保存后应回到商品列表页
            assert "goods-list" in current_url, (
                f"保存后未返回商品列表页，当前URL: {current_url}"
            )

        with allure.step(f"搜索商品: {product_name}"):
            product_page.search_product(product_name)

        with allure.step("断言商品存在于列表中"):
            found = product_page.is_product_in_list(product_name)
            if not found:
                product_page.screenshot("product_not_found_in_list")
            assert found, (
                f"新增的商品 '{product_name}' 未在商品列表中找到"
            )
            logger.info(f"断言通过: 商品 '{product_name}' 已成功新增并可搜索到")

        allure.attach(
            product_name,
            name="新增商品名称",
            attachment_type=allure.attachment_type.TEXT,
        )
