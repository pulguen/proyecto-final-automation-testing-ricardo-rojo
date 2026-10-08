"""TC-03, TC-04 y TC-05: catálogo, interfaz y detalle de producto."""

def test_catalogo_productos(inventory_page):
    """TC-03 (alta): el catálogo muestra productos con nombre y precio."""
    assert inventory_page.get_browser_title() == "Swag Labs", (
        "El título de la pestaña debe ser Swag Labs"
    )
    assert inventory_page.get_title() == "Products", (
        "El encabezado del catálogo debe ser Products"
    )

    products = inventory_page.get_visible_products()
    assert len(products) > 0, "El catálogo debe mostrar al menos un producto"

    first_product_name = inventory_page.get_first_product_name()
    first_product_price = inventory_page.get_first_product_price()
    assert first_product_name, "El nombre del primer producto no debe estar vacío"
    assert first_product_price, "El precio del primer producto no debe estar vacío"

    print(f"Primer producto: {first_product_name}")
    print(f"Precio: {first_product_price}")


def test_elementos_interfaz(inventory_page):
    """TC-04 (media): los controles principales del inventario están visibles."""
    assert inventory_page.is_menu_visible(), "El menú hamburguesa debe estar visible"
    assert inventory_page.is_sort_visible(), "El filtro de productos debe estar visible"
    assert inventory_page.is_cart_visible(), "El carrito debe estar visible"


def test_detalle_primer_producto(inventory_page):
    """TC-05 (media): el detalle corresponde al producto elegido en el catálogo."""
    first_product_name = inventory_page.get_first_product_name()

    inventory_page.open_first_product()
    inventory_page.wait_until_detail_loaded()
    detail_name = inventory_page.get_detail_name()
    detail_price = inventory_page.get_detail_price()
    detail_description = inventory_page.get_detail_description()

    assert detail_name == first_product_name, (
        f"Se esperaba el detalle de {first_product_name!r}, pero se obtuvo {detail_name!r}"
    )
    assert detail_price, "El precio del detalle no debe estar vacío"
    assert detail_description, "La descripción del detalle no debe estar vacía"
