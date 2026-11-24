"""Fixtures compartidas y registro centralizado de ejecución y fallos."""

import logging
import os
from datetime import datetime
from tempfile import mkdtemp
from pathlib import Path

import pytest
import requests
from selenium import webdriver

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.helpers import save_failure_screenshot
from utils.config import (
    SELENIUM_CACHE_DIR,
    get_api_base_url,
    get_api_timeout,
    get_api_response_limit,
    get_evidence_root,
    resolve_path,
)


logger = logging.getLogger(__name__)


def _new_output_file(value, default):
    path = resolve_path(value) if value else default
    if path.exists():
        raise pytest.UsageError(f"La salida ya existe; elegi otro archivo: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    # Configurar las rutas antes de que logging y pytest-html abran sus archivos.
    try:
        output_root = get_evidence_root(config.getoption("output_dir"))
    except ValueError as error:
        raise pytest.UsageError(str(error)) from error
    output_root.mkdir(parents=True, exist_ok=True)
    prefix = datetime.now().strftime("%Y%m%d_%H%M%S_")
    run_dir = Path(mkdtemp(prefix=prefix, dir=output_root))
    (run_dir / "screenshots").mkdir()
    config._evidence_dir = run_dir
    config.option.log_file = _new_output_file(
        config.getoption("log_file") or config.getini("log_file"),
        run_dir / "logs" / "execution.log",
    )
    config.option.htmlpath = _new_output_file(
        config.getoption("htmlpath"), run_dir / "reporte.html",
    )
    if config.option.log_file == config.option.htmlpath:
        raise pytest.UsageError("El log y el reporte HTML deben usar archivos diferentes")
    config.option.self_contained_html = True


def pytest_report_header(config):
    return [
        f"Evidencias: {config._evidence_dir}",
        f"Log: {config.option.log_file}",
        f"HTML: {config.option.htmlpath}",
    ]


def pytest_sessionstart(session):
    logger.info("Inicio de ejecución en %s", session.config.rootpath)
    logger.info("Evidencias de esta ejecucion: %s", session.config._evidence_dir)


def pytest_runtest_logstart(nodeid, location):
    logger.info("Iniciando %s", nodeid)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Primero Pytest determina el resultado de la preparación, test o cierre.
    outcome = yield
    report = outcome.get_result()

    if report.failed:
        logger.error(
            "FALLO en %s (fase %s)\n%s",
            item.nodeid, report.when, report.longreprtext,
        )
        if "driver" in item.fixturenames:
            save_failure_screenshot(
                item.funcargs.get("driver"), item.name, report.when,
                item.config._evidence_dir / "screenshots",
            )
    elif report.when == "call" or report.skipped:
        logger.info("Resultado %s: %s", item.nodeid, report.outcome.upper())


def pytest_runtest_logfinish(nodeid, location):
    logger.info("Finalizando %s", nodeid)


def pytest_sessionfinish(session, exitstatus):
    logger.info(
        "Fin de ejecución: código %s; tests con fallos: %s",
        exitstatus, session.testsfailed,
    )


def pytest_addoption(parser):
    parser.addoption(
        "--output-dir",
        default=None,
        help="Directorio base de evidencias; prevalece sobre EVIDENCE_DIR.",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        help="Ejecutar Chrome sin abrir una ventana visible.",
    )


@pytest.fixture
def driver(request):
    # Selenium Manager guarda el driver dentro del proyecto, no en el perfil del usuario.
    cache = SELENIUM_CACHE_DIR
    cache.mkdir(parents=True, exist_ok=True)
    os.environ["SE_CACHE_PATH"] = str(cache)

    options = webdriver.ChromeOptions()
    if request.config.getoption("--headless"):
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1440,900")

    logger.info("Abriendo Chrome (headless=%s)", request.config.getoption("--headless"))
    browser = webdriver.Chrome(options=options)
    try:
        if not request.config.getoption("--headless"):
            browser.maximize_window()
        yield browser
    finally:
        logger.info("Cerrando Chrome para %s", request.node.name)
        browser.quit()


@pytest.fixture
def inventory_page(driver):
    """Cada test inicia sesión con el navegador nuevo de la fixture driver."""
    login_page = LoginPage(driver)
    login_page.open()
    logger.info("Iniciando sesión con standard_user para preparar el inventario")
    login_page.login("standard_user", "secret_sauce")

    page = InventoryPage(driver)
    page.wait_until_loaded()
    logger.info("Inventario listo: %s", driver.current_url)
    return page


@pytest.fixture
def api_session():
    """Una sesión HTTP aislada por test; se cierra incluso ante fallos."""
    with requests.Session() as session:
        yield session


@pytest.fixture
def api_request(api_session):
    """Enviar solicitudes con timeout y registrar su resultado sin registrar payloads."""
    base_url = get_api_base_url()
    timeout = get_api_timeout()
    response_limit = get_api_response_limit()

    def send(method, endpoint, **kwargs):
        try:
            response = api_session.request(method, base_url + endpoint, timeout=timeout, **kwargs)
        except requests.Timeout as error:
            logger.error("API %s %s: timeout tras %s segundos", method, endpoint, timeout)
            pytest.fail(f"Timeout en {method} {endpoint}: {error}", pytrace=False)
        except requests.ConnectionError as error:
            logger.error("API %s %s: error de conexión: %s", method, endpoint, error)
            pytest.fail(f"Error de conexión en {method} {endpoint}: {error}", pytrace=False)
        except requests.RequestException as error:
            logger.error("API %s %s: error HTTP de transporte: %s", method, endpoint, error)
            pytest.fail(f"Error de transporte en {method} {endpoint}: {error}", pytrace=False)
        elapsed = response.elapsed.total_seconds()
        logger.info("API %s %s: status=%s duracion=%.3fs", method, endpoint, response.status_code, elapsed)
        assert elapsed <= response_limit, (
            f"{method} {endpoint}: {elapsed:.3f}s supera el límite de {response_limit}s"
        )
        return response

    return send
