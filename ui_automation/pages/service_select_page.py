import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class ServiceSelectPage(BasePage):
    """服务/账套/产品选择页面对象"""

    def __init__(self, page: Page, config: dict):
        super().__init__(page, config)

    @allure.step("选择服务: {service_name}")
    def select_service(self, service_name: str):
        """选择指定服务名称"""
        service_locator = self.page.get_by_text(service_name, exact=False)
        self.click(service_locator)
        self.page.wait_for_load_state("networkidle", timeout=self.timeout)

    @allure.step("选择账套: {account_name}")
    def select_account(self, account_name: str):
        """选择指定账套名称"""
        account_locator = self.page.get_by_text(account_name, exact=False)
        self.click(account_locator)
        self.page.wait_for_load_state("networkidle", timeout=self.timeout)

    @allure.step("选择产品: {product_name}")
    def select_product(self, product_name: str):
        """选择指定产品"""
        product_locator = self.page.get_by_text(product_name, exact=False)
        self.click(product_locator)
        self.page.wait_for_load_state("networkidle", timeout=self.timeout)

    @allure.step("完成服务/账套/产品选择")
    def complete_selection(self, service_name: str = None, account_name: str = None, product_name: str = None):
        """组合方法：依次选择服务、账套、产品"""
        service_cfg = self.config.get("service", {})
        service_name = service_name or service_cfg["service_name"]
        account_name = account_name or service_cfg["account_name"]
        product_name = product_name or service_cfg["product_name"]

        self.select_service(service_name)
        self.select_account(account_name)
        self.select_product(product_name)
