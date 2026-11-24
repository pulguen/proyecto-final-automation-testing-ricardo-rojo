"""Escenarios de login parametrizados desde JSON; los casos originales se conservan."""

import pytest

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.data_loader import load_json_cases


pytestmark = pytest.mark.ui
LOGIN_CASES = load_json_cases(
    "data/login_cases.json",
    required_fields=("username", "password", "expected_result", "expected_error"),
    allow_empty_fields=("username", "password", "expected_error"),
)


@pytest.mark.parametrize("case", LOGIN_CASES, ids=lambda case: case["id"])
def test_login_parametrizado(driver, case):
    expected_result = case["expected_result"]
    assert expected_result in ("success", "error"), "expected_result debe ser success o error"
    login_page = LoginPage(driver)
    login_page.open()

    login_page.login(case["username"], case["password"])

    if expected_result == "success":
        inventory_page = InventoryPage(driver)
        inventory_page.wait_until_loaded()
        assert "/inventory.html" in driver.current_url, "El login válido debe abrir el inventario"
        assert inventory_page.get_title() == "Products", "Debe mostrarse el título Products"
        assert inventory_page.get_logo_text() == "Swag Labs", "Debe mostrarse la marca Swag Labs"
    else:
        error_message = login_page.get_error_message()
        assert "/inventory.html" not in driver.current_url, "El login rechazado no debe entrar al inventario"
        assert case["expected_error"], "Los casos de error deben definir expected_error"
        assert error_message == case["expected_error"], (
            f"Mensaje inesperado para {case['id']}: {error_message!r}"
        )
