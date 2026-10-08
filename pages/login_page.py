"""Localizadores y acciones de la pantalla de login de SauceDemo."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    URL = "https://www.saucedemo.com/"
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, '[data-test="error"]')

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self):
        self.driver.get(self.URL)
        self.wait.until(EC.visibility_of_element_located(self.USERNAME))

    def login(self, username, password):
        username_input = self.wait.until(
            EC.visibility_of_element_located(self.USERNAME)
        )
        username_input.clear()
        username_input.send_keys(username)

        password_input = self.wait.until(
            EC.visibility_of_element_located(self.PASSWORD)
        )
        password_input.clear()
        password_input.send_keys(password)

        self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON)).click()

    def get_error_message(self):
        return self.wait.until(
            EC.visibility_of_element_located(self.ERROR_MESSAGE)
        ).text
