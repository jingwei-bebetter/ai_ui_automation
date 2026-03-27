"""商品页面对象 - 商品列表、新增商品表单、搜索"""
import logging
import time
from typing import Optional

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ProductPage(BasePage):
    """商品管理页面对象：商品列表 + 新增商品表单"""

    # === 商品列表页选择器 ===
    ADD_BUTTON = 'taro-view-core.iconcool.xinzeng2'
    SEARCH_INPUT = 'input[placeholder*="搜索商品名称"]'
    GOODS_ITEM = 'taro-view-core.quick-add-goods-item-panel'

    # === 新增表单选择器 ===
    FORM_ROW = 'taro-view-core.jdy-list-item-wrapper'
    FORM_TITLE = 'taro-view-core.title'
    FOOTER_BTN = 'taro-view-core.footer-button-list__btn'

    # === 浮层相关 ===
    OVERLAY_SELECTORS = (
        '.at-float-layout__overlay, .tipcon, .tipcon_content, '
        '[class*="at-float-layout--active"]'
    )

    def __init__(self, page: Page, config: dict):
        super().__init__(page, config)

    # ---------- 浮层处理 ----------

    @allure.step("CSS隐藏浮层遮罩")
    def hide_overlays(self):
        """CSS隐藏浮层但不移除DOM，保持Taro组件树完整"""
        count = self.page.evaluate(f"""() => {{
            let count = 0;
            document.querySelectorAll('{self.OVERLAY_SELECTORS}').forEach(el => {{
                el.style.pointerEvents = 'none';
                el.style.opacity = '0';
                el.style.zIndex = '-1';
                count++;
            }});
            return count;
        }}""")
        if count > 0:
            logger.info(f"CSS隐藏了 {count} 个浮层元素")
        self.page.wait_for_timeout(300)

    # ---------- 等待辅助 ----------

    def _wait_for_form(self, timeout: int = None):
        """等待新增表单加载完成（商品名称行可见）"""
        timeout = timeout or self.timeout
        self.page.locator(
            f'{self.FORM_ROW}:has-text("商品名称")'
        ).first.wait_for(state="visible", timeout=timeout)

    def _wait_for_url_contains(self, fragment: str, timeout: int = None):
        """等待URL包含指定片段"""
        timeout = timeout or self.timeout
        self.page.wait_for_url(f"**{fragment}**", timeout=timeout)

    def _select_list_item(self, text: str, timeout: int = 5000):
        """在 basedata/list 选择页中点击指定文本的选项"""
        self.page.wait_for_timeout(1000)
        items = self.page.locator('taro-view-core, taro-text-core')
        count = items.count()
        for i in range(count):
            try:
                el = items.nth(i)
                if el.is_visible(timeout=200):
                    el_text = el.text_content().strip()
                    if el_text == text:
                        el.click()
                        logger.info(f"已选择列表项: '{text}'")
                        return True
            except Exception:
                continue
        logger.warning(f"未找到列表项: '{text}'")
        self.screenshot(f"select_list_item_not_found_{text}")
        return False

    # ---------- 商品列表页操作 ----------

    @allure.step("点击新增商品按钮")
    def click_add_product(self):
        """在商品列表页点击右上角⊕进入新增页面"""
        add_btn = self.page.locator(self.ADD_BUTTON).first
        add_btn.click(force=True)
        self.page.wait_for_timeout(3000)
        self._wait_for_form()
        self.hide_overlays()
        logger.info("已进入新增商品页面")

    @allure.step("搜索商品: {keyword}")
    def search_product(self, keyword: str):
        """在商品列表页搜索商品"""
        search = self.page.locator(self.SEARCH_INPUT)
        search.first.wait_for(state="visible", timeout=self.timeout)
        search.first.fill(keyword)
        # 触发搜索（模拟回车或等待自动搜索）
        search.first.press("Enter")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        logger.info(f"已搜索: {keyword}")

    @allure.step("获取商品列表中的商品名称")
    def get_goods_names(self) -> list:
        """获取当前商品列表中所有商品名称"""
        items = self.page.locator(self.GOODS_ITEM)
        names = []
        count = items.count()
        for i in range(count):
            try:
                text = items.nth(i).text_content().strip()
                if text:
                    names.append(text)
            except Exception:
                continue
        logger.info(f"商品列表获取到 {len(names)} 个商品")
        return names

    @allure.step("检查商品是否存在: {product_name}")
    def is_product_in_list(self, product_name: str) -> bool:
        """检查商品列表中是否存在指定名称的商品"""
        page_text = self.page.locator(
            f'{self.GOODS_ITEM}:has-text("{product_name}")'
        )
        exists = page_text.count() > 0
        logger.info(f"商品 '{product_name}' 存在: {exists}")
        return exists

    # ---------- 新增表单操作 ----------

    @allure.step("填写商品名称: {name}")
    def fill_product_name(self, name: str):
        """填写商品名称字段"""
        name_input = self.page.locator(
            f'{self.FORM_ROW}:has-text("商品名称") input'
        )
        name_input.fill(name)
        self.page.wait_for_timeout(300)
        logger.info(f"填写商品名称: {name}")

    @allure.step("选择商品类别: {category_name}")
    def select_category(self, category_name: str):
        """点击商品类别字段并在选择页中选择指定类别"""
        # 点击商品类别行
        self.page.locator(
            f'{self.FORM_ROW}:has-text("商品类别")'
        ).first.click()
        self.page.wait_for_timeout(2000)
        logger.info(f"已进入商品类别选择页: {self.page.url}")

        # 选择类别
        self._select_list_item(category_name)

        # 等待返回编辑页
        self._wait_for_url_contains("/good-edit/index")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

        # 等待表单渲染
        self._wait_for_form()
        self.hide_overlays()
        logger.info(f"已选择商品类别: {category_name}")

    @allure.step("选择计量单位: {unit_name}")
    def select_unit(self, unit_name: str):
        """点击计量单位字段并选择指定单位（两层导航）"""
        # 第1层: 点击计量单位行 -> 进入单位设置页
        self.page.locator(
            f'{self.FORM_ROW}:has-text("计量单位")'
        ).first.click()
        self.page.wait_for_timeout(2000)
        logger.info(f"已进入单位设置页: {self.page.url}")

        # 第2层: 点击"基本单位"行的"请选择" -> 进入单位列表
        self.page.locator(
            f'{self.FORM_ROW}:has-text("基本单位")'
        ).first.click()
        self.page.wait_for_timeout(2000)
        logger.info(f"已进入单位列表页: {self.page.url}")

        # 选择单位
        self._select_list_item(unit_name)

        # 等待返回单位设置页
        self._wait_for_url_contains("/unit/index")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)

        # 点击单位设置页的保存按钮
        self._click_visible_button("保存")
        self.page.wait_for_timeout(2000)

        # 等待返回编辑页
        self._wait_for_url_contains("/good-edit/index")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

        # 等待表单渲染
        self._wait_for_form()
        self.hide_overlays()
        logger.info(f"已选择计量单位: {unit_name}")

    def _click_visible_button(self, text: str):
        """点击当前页面中可见的按钮（精确匹配文本）。
        兼容不同页面的按钮 class（edit form 用 footer-button-list__btn，
        unit 页用其他 class）。
        """
        # 搜索所有 taro-view-core 中文本精确匹配的可见元素
        candidates = self.page.locator('taro-view-core, taro-text-core')
        count = candidates.count()
        for i in range(count):
            try:
                el = candidates.nth(i)
                if el.is_visible(timeout=200):
                    el_text = el.text_content().strip()
                    if el_text == text:
                        box = el.bounding_box()
                        # 按钮通常在页面底部(y > 700)
                        if box and box['y'] > 700:
                            el.click()
                            logger.info(f"已点击按钮: '{text}' at y={box['y']:.0f}")
                            return
            except Exception:
                continue
        # fallback: 用 get_by_text
        logger.warning(f"遍历未找到按钮'{text}'，尝试 get_by_text")
        self.page.get_by_text(text, exact=True).last.click()

    @allure.step("点击保存按钮")
    def click_save(self, return_url: str = None):
        """点击表单底部的保存按钮，保存后导航回商品列表"""
        self._click_visible_button("保存")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(3000)

        # 保存后如果仍在编辑页，强制整页刷新到商品列表
        # Taro hash SPA路由守卫会阻止同源hash导航，
        # 需添加缓存参数使Playwright视为不同URL触发整页加载
        if "good-edit" in self.page.url and return_url:
            logger.info(f"保存后仍在编辑页，强制整页刷新到: {return_url}")
            parts = return_url.split('#', 1)
            sep = '&' if '?' in parts[0] else '?'
            fresh_url = f"{parts[0]}{sep}_r={int(time.time())}"
            if len(parts) > 1:
                fresh_url += f"#{parts[1]}"
            self.page.goto(fresh_url, wait_until="networkidle")
            self.page.wait_for_timeout(3000)
        logger.info(f"保存完成，当前URL: {self.page.url}")

    # ---------- 组合方法 ----------

    @allure.step("新增商品: {product_name}")
    def add_product(self, product_name: str, category: str, unit: str):
        """
        完整的新增商品流程：
        1. 记录当前商品列表URL（用于保存后返回）
        2. 点击⊕进入新增页面
        3. 选择商品类别
        4. 选择计量单位
        5. 填写商品名称（最后填，避免被导航清除）
        6. 点击保存并返回商品列表
        """
        # 记录商品列表URL，保存后直接导航回来
        goods_list_url = self.page.url
        logger.info(f"记录商品列表URL: {goods_list_url}")

        self.click_add_product()

        # 先选择类别（会导航离开再返回）
        self.select_category(category)

        # 选择单位（会导航离开再返回）
        self.select_unit(unit)

        # 最后填写名称（确保不会被导航清除）
        self.fill_product_name(product_name)

        # 保存并返回商品列表
        self.click_save(return_url=goods_list_url)
        logger.info(f"新增商品完成: {product_name}")
