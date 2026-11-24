"""Contrato de JSONPlaceholder: las escrituras son simuladas y no persisten."""

import pytest

pytestmark = pytest.mark.api


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "").lower(), (
        f"Se esperaba Content-Type JSON, recibido: {response.headers.get('Content-Type')!r}"
    )
    try:
        return response.json()
    except ValueError as error:
        pytest.fail(f"La respuesta no contiene JSON válido: {error}", pytrace=False)


def assert_post(post):
    assert isinstance(post, dict), "Cada post debe ser un objeto JSON"
    for field in ("id", "userId"):
        assert type(post.get(field)) is int, f"{field} debe ser un entero"
    for field in ("title", "body"):
        assert isinstance(post.get(field), str), f"{field} debe ser texto"
        assert post[field].strip(), f"{field} no debe estar vacío"


def test_get_post_existente(api_request):
    response = api_request("GET", "/posts/1")
    assert response.status_code == 200, f"GET /posts/1 devolvió {response.status_code}"
    post = assert_json(response)
    assert_post(post)
    assert post["id"] == 1, "El ID del post debe ser 1"


def test_get_publicaciones(api_request):
    response = api_request("GET", "/posts")
    assert response.status_code == 200, f"GET /posts devolvió {response.status_code}"
    posts = assert_json(response)
    assert isinstance(posts, list) and posts, "La respuesta debe ser una lista no vacía"
    for post in posts:
        assert_post(post)


def test_get_publicaciones_filtradas(api_request):
    user_id = 1
    response = api_request("GET", "/posts", params={"userId": user_id})
    assert response.status_code == 200, f"GET /posts filtrado devolvió {response.status_code}"
    posts = assert_json(response)
    assert isinstance(posts, list) and posts, "El filtro debe devolver una lista no vacía"
    for post in posts:
        assert_post(post)
        assert post["userId"] == user_id, "Todos los posts deben pertenecer al usuario solicitado"


def test_get_post_inexistente(api_request):
    response = api_request("GET", "/posts/999999")
    assert response.status_code == 404, f"El recurso inexistente devolvió {response.status_code}, se esperaba 404"
    assert assert_json(response) == {}, "La respuesta observada para el recurso inexistente debe estar vacía"


def test_post_crear_publicacion(api_request):
    payload = {"title": "Prueba API", "body": "Contenido de prueba", "userId": 1}
    response = api_request("POST", "/posts", json=payload)
    assert response.status_code == 201, f"POST /posts devolvió {response.status_code}"
    post = assert_json(response)
    assert_post(post)
    assert post["id"] > 0, "La respuesta debe incluir un ID generado positivo"
    for field, value in payload.items():
        assert post[field] == value, f"El campo {field} no coincide con el enviado"


def test_put_reemplazar_publicacion(api_request):
    payload = {"id": 1, "title": "Titulo actualizado", "body": "Contenido actualizado", "userId": 1}
    response = api_request("PUT", "/posts/1", json=payload)
    assert response.status_code == 200, f"PUT /posts/1 devolvió {response.status_code}"
    post = assert_json(response)
    assert_post(post)
    for field, value in payload.items():
        assert post[field] == value, f"PUT no reflejó el campo {field}"


def test_patch_modificar_titulo(api_request):
    payload = {"title": "Titulo parcial"}
    response = api_request("PATCH", "/posts/1", json=payload)
    assert response.status_code == 200, f"PATCH /posts/1 devolvió {response.status_code}"
    post = assert_json(response)
    assert_post(post)
    assert post["id"] == 1, "PATCH debe responder con el recurso solicitado"
    assert post["title"] == payload["title"], "PATCH debe reflejar el título enviado"


def test_delete_publicacion(api_request):
    response = api_request("DELETE", "/posts/1")
    assert response.status_code == 200, f"DELETE /posts/1 devolvió {response.status_code}, se esperaba 200"
    assert assert_json(response) == {}, "DELETE debe devolver el objeto JSON vacío observado"
