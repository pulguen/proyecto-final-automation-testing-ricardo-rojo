"""Localizadores, lecturas y acciones de la página del carrito."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config import get_selenium_timeout


class CartPage:
    CONTAINER = (By.ID, "cart_contents_container")
    PRODUCTS = (By.CSS_SELECTOR, '[data-test="inventory-item"]')
    PRODUCT_NAME = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')
    REMOVE_BUTTON = (By.CSS_SELECTOR, 'button[id^="remove-"]')
    CART_BADGE = (By.CSS_SELECTOR, '[data-test="shopping-cart-badge"]')

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, get_selenium_timeout())

    def wait_until_loaded(self):
        self.wait.until(EC.url_contains("/cart.html"))
        self.wait.until(EC.visibility_of_element_located(self.CONTAINER))

    def get_product_names(self):
        return [
            product.find_element(*self.PRODUCT_NAME).text.strip()
            for product in self.driver.find_elements(*self.PRODUCTS)
        ]

    def get_product_count(self):
        return len(self.driver.find_elements(*self.PRODUCTS))

    def remove_first_product(self):
        product = self.wait.until(EC.visibility_of_element_located(self.PRODUCTS))
        remove_button = product.find_element(*self.REMOVE_BUTTON)
        self.wait.until(EC.element_to_be_clickable(remove_button)).click()

    def wait_until_empty(self):
        self.wait.until_not(EC.presence_of_all_elements_located(self.PRODUCTS))

    def wait_until_badge_disappears(self):
        # SauceDemo elimina el badge del DOM cuando el carrito queda vacío.
        self.wait.until_not(EC.presence_of_element_located(self.CART_BADGE))

    def is_badge_present(self):
        return bool(self.driver.find_elements(*self.CART_BADGE))
