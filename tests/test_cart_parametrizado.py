"""Un producto por sesión, seleccionado mediante los datos del CSV."""

import pytest

from pages.cart_page import CartPage
from utils.data_loader import load_csv_cases


pytestmark = pytest.mark.ui
CART_CASES = load_csv_cases(
    "data/cart_products.csv", required_fields=("product_name", "expected_badge"),
)


@pytest.mark.parametrize("case", CART_CASES, ids=lambda case: case["id"])
def test_carrito_parametrizado(driver, inventory_page, case):
    product_name = case["product_name"]
    available_names = inventory_page.get_product_names()
    assert product_name in available_names, f"El catálogo debe ofrecer {product_name!r}"

    inventory_page.add_product_by_name(product_name)
    badge = inventory_page.wait_for_cart_badge(case["expected_badge"])
    assert badge == case["expected_badge"], f"Cantidad inesperada en el badge: {badge!r}"

    inventory_page.open_cart()
    cart_page = CartPage(driver)
    cart_page.wait_until_loaded()
    assert "/cart.html" in driver.current_url, "Debe abrirse la página del carrito"
    assert cart_page.get_product_count() == 1, "Cada escenario debe tener un único producto"
    assert cart_page.get_product_names() == [product_name], (
        f"El carrito debe contener exactamente {product_name!r}"
    )
