"""TC-01 y TC-02: validaciones del login, ambos de prioridad alta."""

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


def test_login_exitoso(driver):
    """TC-01: un usuario válido accede al inventario y ve sus encabezados."""
    login_page = LoginPage(driver)
    login_page.open()

    login_page.login("standard_user", "secret_sauce")
    inventory_page = InventoryPage(driver)
    inventory_page.wait_until_loaded()

    assert "/inventory.html" in driver.current_url, (
        f"Se esperaba el inventario, pero la URL es {driver.current_url}"
    )
    assert inventory_page.get_title() == "Products", (
        "El título visible del inventario debe ser Products"
    )
    assert inventory_page.get_logo_text() == "Swag Labs", (
        "La marca Swag Labs debe estar visible en el inventario"
    )


def test_login_credenciales_invalidas(driver):
    """TC-02: una contraseña incorrecta muestra el error correspondiente."""
    login_page = LoginPage(driver)
    login_page.open()

    login_page.login("standard_user", "clave_incorrecta")
    # Esperar el error evita validar la URL antes de que se procese el login.
    error_message = login_page.get_error_message()

    assert "/inventory.html" not in driver.current_url, (
        "Las credenciales inválidas no deben permitir entrar al inventario"
    )
    assert error_message == (
        "Epic sadface: Username and password do not match any user in this service"
    ), f"El mensaje no corresponde a credenciales inválidas: {error_message!r}"
