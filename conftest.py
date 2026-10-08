"""Fixtures compartidas y registro centralizado de ejecución y fallos."""

import logging
import os
from pathlib import Path

import pytest
from selenium import webdriver

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.helpers import save_failure_screenshot


logger = logging.getLogger(__name__)


def pytest_sessionstart(session):
    logger.info("Inicio de ejecución en %s", session.config.rootpath)


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
        save_failure_screenshot(item.funcargs.get("driver"), item.name, report.when)
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
        "--headless",
        action="store_true",
        help="Ejecutar Chrome sin abrir una ventana visible.",
    )


@pytest.fixture
def driver(request):
    # Selenium Manager guarda el driver dentro del proyecto, no en el perfil del usuario.
    cache = Path(__file__).parent / ".tools" / "selenium"
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
