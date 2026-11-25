"""Tres flujos UI instrumentados sin modificar los tests funcionales."""

import json
import logging
import os
import sys
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TARGET_ROOT = Path(os.environ["TARGET_ROOT"]).resolve()
sys.path.insert(0, str(TARGET_ROOT))

from pages.cart_page import CartPage  # noqa: E402
from pages.inventory_page import InventoryPage  # noqa: E402
from pages.login_page import LoginPage  # noqa: E402


logger = logging.getLogger(__name__)


def _state(driver, target=None):
    return driver.execute_script(
        """
        const target = arguments[0];
        const rect = target ? target.getBoundingClientRect() : null;
        const x = rect ? Math.floor(rect.left + rect.width / 2) : null;
        const y = rect ? Math.floor(rect.top + rect.height / 2) : null;
        const atPoint = x === null ? null : document.elementFromPoint(x, y);
        const describe = element => element ? {
          tag: element.tagName,
          id: element.id || "",
          class: typeof element.className === "string" ? element.className : "",
          text: (element.innerText || element.textContent || "").trim().slice(0, 120),
          visible: !!(element.offsetWidth || element.offsetHeight || element.getClientRects().length),
          enabled: !element.disabled
        } : null;
        const resources = performance.getEntriesByType("resource")
          .filter(entry => entry.name.includes("saucedemo.com"))
          .map(entry => ({name: entry.name.split("?")[0], duration: Math.round(entry.duration)}))
          .slice(-30);
        return {
          url: location.href,
          ready_state: document.readyState,
          target: describe(target),
          target_rect: rect ? {x: rect.x, y: rect.y, width: rect.width, height: rect.height} : null,
          element_at_click: describe(atPoint),
          target_is_at_click: !!(target && atPoint && (atPoint === target || target.contains(atPoint))),
          add_buttons: Array.from(document.querySelectorAll('button[id^="add-to-cart-"]')).map(describe),
          remove_buttons: Array.from(document.querySelectorAll('button[id^="remove-"]')).map(describe),
          cart_badges: Array.from(document.querySelectorAll('[data-test="shopping-cart-badge"]')).map(describe),
          resources
        };
        """,
        target,
    )


def _browser_diagnostics(driver):
    try:
        browser_log = driver.get_log("browser")[-20:]
    except Exception as error:
        browser_log = [{"read_error": type(error).__name__}]
    network_errors = []
    try:
        for entry in driver.get_log("performance")[-100:]:
            message = json.loads(entry["message"])["message"]
            if message.get("method") == "Network.loadingFailed":
                network_errors.append({
                    "method": message["method"],
                    "error": message.get("params", {}).get("errorText"),
                    "type": message.get("params", {}).get("type"),
                })
            if message.get("method") == "Network.responseReceived":
                response = message.get("params", {}).get("response", {})
                if response.get("status", 0) >= 400:
                    network_errors.append({
                        "method": message["method"],
                        "status": response.get("status"),
                        "url": response.get("url", "").split("?")[0],
                    })
    except Exception as error:
        network_errors.append({"read_error": type(error).__name__})
    return {"browser_log": browser_log, "network_errors": network_errors}


def _record(driver, label, target=None):
    data = {"label": label, "state": _state(driver, target), "browser": _browser_diagnostics(driver)}
    logger.info("DIAGNOSTIC %s", json.dumps(data, ensure_ascii=False))
    return data


def _inventory(driver):
    login = LoginPage(driver)
    login.open()
    login.login("standard_user", "secret_sauce")
    inventory = InventoryPage(driver)
    inventory.wait_until_loaded()
    _record(driver, "inventory_loaded")
    return inventory


def _click_and_wait(driver, wait, locator, label, condition):
    element = wait.until(EC.element_to_be_clickable(locator))
    _record(driver, f"before_{label}", element)
    try:
        element.click()
    except Exception:
        _record(driver, f"after_{label}_click_exception")
        raise
    _record(driver, f"after_{label}")
    wait.until(condition)


def test_diagnostico_agregar_producto(driver):
    inventory = _inventory(driver)
    product = inventory.get_visible_products()[0]
    button = product.find_element(*inventory.ADD_BUTTON)
    add_id = button.get_attribute("id")
    remove_id = add_id.replace("add-to-cart-", "remove-", 1)
    _click_and_wait(
        driver,
        WebDriverWait(driver, 10),
        (By.ID, add_id),
        "add_product",
        EC.visibility_of_element_located((By.ID, remove_id)),
    )


def test_diagnostico_abrir_carrito(driver):
    inventory = _inventory(driver)
    product = inventory.get_visible_products()[0]
    button = product.find_element(*inventory.ADD_BUTTON)
    add_id = button.get_attribute("id")
    remove_id = add_id.replace("add-to-cart-", "remove-", 1)
    wait = WebDriverWait(driver, 10)
    _click_and_wait(driver, wait, (By.ID, add_id), "add_before_cart", EC.visibility_of_element_located((By.ID, remove_id)))
    _click_and_wait(driver, wait, inventory.CART_LINK, "open_cart", EC.url_contains("/cart.html"))
    CartPage(driver).wait_until_loaded()


def test_diagnostico_abrir_detalle(driver):
    inventory = _inventory(driver)
    _click_and_wait(driver, WebDriverWait(driver, 10), inventory.PRODUCT_NAME, "open_detail", EC.url_contains("/inventory-item.html"))
