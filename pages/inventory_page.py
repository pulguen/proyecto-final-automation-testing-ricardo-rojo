"""Localizadores, acciones y lecturas del catálogo y del detalle de producto."""

import logging

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config import get_selenium_timeout


logger = logging.getLogger(__name__)


class InventoryPage:
    TITLE = (By.CSS_SELECTOR, '[data-test="title"]')
    LOGO = (By.CLASS_NAME, "app_logo")
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    SORT_SELECT = (By.CSS_SELECTOR, '[data-test="product-sort-container"]')
    CART_LINK = (By.CSS_SELECTOR, '[data-test="shopping-cart-link"]')
    PRODUCT_LIST = (By.CSS_SELECTOR, '[data-test="inventory-list"]')
    PRODUCTS = (By.CSS_SELECTOR, '[data-test="inventory-item"]')
    PRODUCT_NAME = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')
    PRODUCT_PRICE = (By.CSS_SELECTOR, '[data-test="inventory-item-price"]')
    PRODUCT_DESCRIPTION = (By.CSS_SELECTOR, '[data-test="inventory-item-desc"]')
    DETAIL_CONTAINER = (By.ID, "inventory_item_container")
    ADD_BUTTON = (By.CSS_SELECTOR, 'button[id^="add-to-cart-"]')
    CART_BADGE = (By.CSS_SELECTOR, '[data-test="shopping-cart-badge"]')

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, get_selenium_timeout())
        self._last_add = None

    def wait_until_loaded(self):
        self.wait.until(EC.url_contains("/inventory.html"))
        self.wait.until(EC.visibility_of_element_located(self.TITLE))

    def get_title(self):
        return self.wait.until(EC.visibility_of_element_located(self.TITLE)).text

    def get_logo_text(self):
        return self.wait.until(EC.visibility_of_element_located(self.LOGO)).text

    def get_browser_title(self):
        return self.driver.title

    def get_visible_products(self):
        self.wait.until(EC.visibility_of_element_located(self.PRODUCT_LIST))
        products = self.driver.find_elements(*self.PRODUCTS)
        return [product for product in products if product.is_displayed()]

    def get_first_product_name(self):
        first_product = self.get_visible_products()[0]
        return first_product.find_element(*self.PRODUCT_NAME).text.strip()

    def get_first_product_price(self):
        first_product = self.get_visible_products()[0]
        return first_product.find_element(*self.PRODUCT_PRICE).text.strip()

    def get_product_names(self):
        return [
            product.find_element(*self.PRODUCT_NAME).text.strip()
            for product in self.get_visible_products()
        ]

    def add_product(self, index):
        """Agregar un producto según su lugar en el catálogo, empezando en cero."""
        product = self.get_visible_products()[index]
        self._add_product(product)

    def add_product_by_name(self, product_name):
        """Seleccionar por nombre exacto, sin fijar su posición en el catálogo."""
        for product in self.get_visible_products():
            if product.find_element(*self.PRODUCT_NAME).text.strip() == product_name:
                self._add_product(product)
                return
        raise NoSuchElementException(f"Producto no disponible en el catálogo: {product_name!r}")

    def _add_product(self, product):
        """Compartir el clic y la confirmación de Remove entre ambas formas de selección."""
        product_name = product.find_element(*self.PRODUCT_NAME).text
        add_button = product.find_element(*self.ADD_BUTTON)
        add_id = add_button.get_attribute("id")
        add_locator = (By.ID, add_id)
        remove_locator = (By.ID, add_id.replace("add-to-cart-", "remove-", 1))
        self._last_add = (add_id, add_button)
        logger.info(
            "ANTES click: url=%s producto=%r texto=%r visible=%s habilitado=%s",
            self.driver.current_url, product_name,
            add_button.text, add_button.is_displayed(), add_button.is_enabled(),
        )
        try:
            # Relocalizar por ID evita depender del WebElement leído anteriormente.
            add_button = self.wait.until(EC.element_to_be_clickable(add_locator))
            self._last_add = (add_id, add_button)
            add_button.click()
            self._log_cart_state("DESPUES click")
            # El botón Remove confirma que la aplicación procesó la acción.
            self.wait.until(EC.visibility_of_element_located(remove_locator))
            logger.info("Producto agregado confirmado por Remove: %s", product_name)
        except WebDriverException:
            self._log_cart_state("ERROR al agregar o esperar Remove")
            raise

    def _log_cart_state(self, stage):
        """Registrar el estado de la última acción sin ocultar el error original."""
        if self._last_add is None:
            return
        try:
            add_id, original_button = self._last_add
            remove_id = add_id.replace("add-to-cart-", "remove-", 1)
            add_buttons = self.driver.find_elements(By.ID, add_id)
            remove_buttons = self.driver.find_elements(By.ID, remove_id)
            badges = self.driver.find_elements(*self.CART_BADGE)
            try:
                original_state = original_button.get_attribute("id")
            except StaleElementReferenceException:
                original_state = "STALE"
            logger.info(
                "%s: url=%s add=%s remove=%s badge=%s original=%s",
                stage, self.driver.current_url,
                [(b.text, b.is_displayed()) for b in add_buttons],
                [(b.text, b.is_displayed()) for b in remove_buttons],
                [(b.text, b.is_displayed()) for b in badges], original_state,
            )
        except WebDriverException as error:
            logger.warning("Diagnóstico no disponible (%s): %s", stage, error)

    def wait_for_cart_badge(self, expected_count):
        try:
            self.wait.until(EC.visibility_of_element_located(self.CART_BADGE))
            # Esperar igualdad exacta: no confundir, por ejemplo, 1 con 10.
            self.wait.until(
                lambda driver: driver.find_element(*self.CART_BADGE).text
                == str(expected_count)
            )
        except WebDriverException:
            self._log_cart_state("ERROR espera badge")
            raise
        return self.driver.find_element(*self.CART_BADGE).text

    def open_cart(self):
        self.wait.until(EC.element_to_be_clickable(self.CART_LINK)).click()

    def is_menu_visible(self):
        return self.wait.until(
            EC.visibility_of_element_located(self.MENU_BUTTON)
        ).is_displayed()

    def is_sort_visible(self):
        return self.wait.until(
            EC.visibility_of_element_located(self.SORT_SELECT)
        ).is_displayed()

    def is_cart_visible(self):
        return self.wait.until(
            EC.visibility_of_element_located(self.CART_LINK)
        ).is_displayed()

    def open_first_product(self):
        first_product = self.get_visible_products()[0]
        product_name = first_product.find_element(*self.PRODUCT_NAME)
        self.wait.until(EC.element_to_be_clickable(product_name)).click()

    def wait_until_detail_loaded(self):
        self.wait.until(EC.url_contains("/inventory-item.html"))
        self.wait.until(EC.visibility_of_element_located(self.DETAIL_CONTAINER))

    # El catálogo y el detalle comparten estos atributos data-test.
    def get_detail_name(self):
        return self.wait.until(
            EC.visibility_of_element_located(self.PRODUCT_NAME)
        ).text.strip()

    def get_detail_price(self):
        return self.wait.until(
            EC.visibility_of_element_located(self.PRODUCT_PRICE)
        ).text.strip()

    def get_detail_description(self):
        return self.wait.until(
            EC.visibility_of_element_located(self.PRODUCT_DESCRIPTION)
        ).text.strip()
