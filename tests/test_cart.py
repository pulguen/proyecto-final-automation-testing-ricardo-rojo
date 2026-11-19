"""TC-06, TC-07 y TC-08: incorporación y eliminación de productos del carrito."""

import pytest

from pages.cart_page import CartPage


pytestmark = pytest.mark.ui


def test_agregar_producto_carrito(driver, inventory_page):
    """TC-06 (alta): el carrito contiene el mismo producto que se agregó."""
    product_name = inventory_page.get_first_product_name()

    inventory_page.add_product(0)
    badge = inventory_page.wait_for_cart_badge(1)
    assert badge == "1", f"El badge debe mostrar 1, pero muestra {badge!r}"

    inventory_page.open_cart()
    cart_page = CartPage(driver)
    cart_page.wait_until_loaded()
    product_names = cart_page.get_product_names()

    assert "/cart.html" in driver.current_url, (
        f"Se esperaba la página del carrito, pero la URL es {driver.current_url}"
    )
    assert product_names == [product_name], (
        f"El carrito debe contener solo {product_name!r}, pero contiene {product_names!r}"
    )


def test_agregar_dos_productos(driver, inventory_page):
    """TC-07 (media): el badge y el contenido reflejan dos productos distintos."""
    available_names = inventory_page.get_product_names()
    assert len(available_names) >= 2, "Se necesitan al menos dos productos disponibles"
    expected_names = available_names[:2]

    inventory_page.add_product(0)
    inventory_page.add_product(1)
    badge = inventory_page.wait_for_cart_badge(2)
    assert badge == "2", f"El badge debe mostrar 2, pero muestra {badge!r}"

    inventory_page.open_cart()
    cart_page = CartPage(driver)
    cart_page.wait_until_loaded()
    product_names = cart_page.get_product_names()

    assert cart_page.get_product_count() == 2, (
        f"El carrito debe contener exactamente dos productos: {product_names!r}"
    )
    for name in expected_names:
        assert name in product_names, f"Falta el producto {name!r} en el carrito"


def test_eliminar_producto_carrito(driver, inventory_page):
    """TC-08 (media): eliminar el único producto deja el carrito vacío y sin badge."""
    product_name = inventory_page.get_first_product_name()
    inventory_page.add_product(0)
    badge = inventory_page.wait_for_cart_badge(1)
    assert badge == "1", f"El badge debe mostrar 1, pero muestra {badge!r}"

    inventory_page.open_cart()
    cart_page = CartPage(driver)
    cart_page.wait_until_loaded()
    assert cart_page.get_product_count() == 1, (
        "Debe haber un producto en el carrito antes de eliminarlo"
    )
    assert product_name in cart_page.get_product_names(), (
        f"El producto {product_name!r} debe estar en el carrito antes de eliminarlo"
    )

    cart_page.remove_first_product()
    cart_page.wait_until_empty()
    cart_page.wait_until_badge_disappears()

    assert cart_page.get_product_count() == 0, "El carrito debe quedar vacío"
    assert product_name not in cart_page.get_product_names(), (
        f"El producto {product_name!r} debe desaparecer del carrito"
    )
    assert not cart_page.is_badge_present(), (
        "El badge debe desaparecer del DOM cuando el carrito queda vacío"
    )
