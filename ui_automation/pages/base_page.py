import logging
import os
import re
from typing import List, Union

import allure
from playwright.sync_api import Locator, Page

logger = logging.getLogger(__name__)


class BasePage:
    """基础页面类，统一封装所有元素交互方法"""

    def __init__(self, page: Page, config: dict):
        self.page = page
        self.config = config
        self.timeout = config.get("timeout", 15000)

    def _resolve_locator(self, locator_or_str: Union[str, Locator]) -> Locator:
        """统一将字符串或 Locator 对象转换为 Locator"""
        if isinstance(locator_or_str, str):
            return self.page.locator(locator_or_str)
        return locator_or_str

    def click(self, locator: Union[str, Locator], timeout: int = None, **kwargs):
        """点击元素，自动等待可见+可点击"""
        timeout = timeout or self.timeout
        loc = self._resolve_locator(locator)
        desc = self._locator_desc(locator)
        with allure.step(f"点击: {desc}"):
            logger.info(f"点击元素: {desc}")
            try:
                loc.click(timeout=timeout, **kwargs)
            except Exception as e:
                self.screenshot(f"click_failed_{desc}")
                raise

    def fill(self, locator: Union[str, Locator], text: str, timeout: int = None, **kwargs):
        """清空并输入文本"""
        timeout = timeout or self.timeout
        loc = self._resolve_locator(locator)
        desc = self._locator_desc(locator)
        with allure.step(f"输入: {desc} <- '{text}'"):
            logger.info(f"输入文本: {desc} <- '{text}'")
            try:
                loc.fill(text, timeout=timeout, **kwargs)
            except Exception as e:
                self.screenshot(f"fill_failed_{desc}")
                raise

    def get_text(self, locator: Union[str, Locator], timeout: int = None) -> str:
        """获取单个元素文本内容"""
        timeout = timeout or self.timeout
        loc = self._resolve_locator(locator)
        loc.wait_for(state="visible", timeout=timeout)
        text = loc.text_content() or ""
        return text.strip()

    def get_texts(self, locator: Union[str, Locator], timeout: int = None) -> List[str]:
        """获取所有匹配元素的文本列表"""
        timeout = timeout or self.timeout
        loc = self._resolve_locator(locator)
        loc.first.wait_for(state="visible", timeout=timeout)
        elements = loc.all()
        texts = []
        for el in elements:
            text = el.text_content() or ""
            text = text.strip()
            if text:
                texts.append(text)
        return texts

    def wait_for_element(self, locator: Union[str, Locator], state: str = "visible", timeout: int = None):
        """显式等待元素状态"""
        timeout = timeout or self.timeout
        loc = self._resolve_locator(locator)
        loc.wait_for(state=state, timeout=timeout)

    def is_visible(self, locator: Union[str, Locator], timeout: int = 3000) -> bool:
        """判断元素是否可见（不抛异常）"""
        try:
            loc = self._resolve_locator(locator)
            loc.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def scroll_to(self, locator: Union[str, Locator]):
        """滚动到元素可见"""
        loc = self._resolve_locator(locator)
        loc.scroll_into_view_if_needed()

    def screenshot(self, name: str) -> str:
        """截图并附加到 allure 报告"""
        # 清理文件名中的非法字符（Windows 不允许 < > : " / \ | ? *）
        safe_name = re.sub(r'[<>:"/\\|?*\s]', '_', name)[:100]
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        screenshot_dir = os.path.join(project_root, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        path = os.path.join(screenshot_dir, f"{safe_name}.png")
        self.page.screenshot(path=path)
        allure.attach.file(path, name=name, attachment_type=allure.attachment_type.PNG)
        logger.info(f"截图已保存: {path}")
        return path

    @staticmethod
    def _locator_desc(locator: Union[str, Locator]) -> str:
        """获取 locator 的描述信息（用于日志）"""
        if isinstance(locator, str):
            return locator
        try:
            return str(locator)
        except Exception:
            return "unknown_locator"
