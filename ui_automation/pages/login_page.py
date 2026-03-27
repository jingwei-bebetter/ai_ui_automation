import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    """登录页面对象"""

    # 定位器 - 根据实际页面结构调整
    PHONE_INPUT = 'input[type="tel"], input[placeholder*="手机"], input[placeholder*="账号"], input[name="phone"]'
    PASSWORD_INPUT = 'input[type="password"]'
    AGREE_CHECKBOX = 'text=同意'
    # 使用 role=button 精确匹配登录按钮，避免匹配页面标题"密码登录"
    LOGIN_BUTTON = 'role=button[name="登录"]'

    def __init__(self, page: Page, config: dict):
        super().__init__(page, config)
        self.base_url = config.get("base_url", "https://sale.jdy.com")

    @allure.step("打开登录页面")
    def navigate(self):
        """访问登录地址"""
        self.page.goto(self.base_url, wait_until="domcontentloaded")
        self.page.wait_for_load_state("networkidle", timeout=self.timeout)

    @allure.step("输入手机号: {phone}")
    def enter_phone(self, phone: str):
        """输入手机号"""
        self.fill(self.PHONE_INPUT, phone)

    @allure.step("输入密码")
    def enter_password(self, password: str):
        """输入密码"""
        self.fill(self.PASSWORD_INPUT, password)

    @allure.step("勾选同意协议")
    def agree_terms(self):
        """勾选同意协议复选框"""
        # 尝试多种定位方式找到同意复选框并勾选
        agree_locator = self.page.locator(self.AGREE_CHECKBOX)
        if agree_locator.count() > 0:
            self.click(agree_locator.first)
        else:
            # 备用：尝试通过 checkbox 类型定位
            checkbox = self.page.locator('input[type="checkbox"]')
            if checkbox.count() > 0:
                self.click(checkbox.first)

    @allure.step("点击登录按钮")
    def submit_login(self):
        """点击登录按钮"""
        self.click(self.LOGIN_BUTTON)

    @allure.step("完成登录流程")
    def login(self, phone: str = None, password: str = None):
        """组合方法：完成整个登录流程"""
        phone = phone or self.config["login"]["phone"]
        password = password or self.config["login"]["password"]

        self.navigate()
        self.enter_phone(phone)
        self.enter_password(password)
        self.agree_terms()
        self.submit_login()
        # 等待页面跳转，离开登录页
        self.page.wait_for_load_state("networkidle", timeout=self.timeout)
