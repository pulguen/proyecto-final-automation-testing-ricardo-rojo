"""Fixtures y evidencias exclusivamente para el diagnóstico temporal de CI."""

import base64
import logging
import os
from datetime import datetime
from html import escape
from pathlib import Path

import pytest
from pytest_html import extras
from selenium import webdriver


logger = logging.getLogger(__name__)


def _output_dir():
    path = Path(os.environ.get("DIAGNOSTIC_OUTPUT", "output")).resolve()
    path.mkdir(parents=True, exist_ok=True)
    (path / "screenshots").mkdir(exist_ok=True)
    return path


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    output = _output_dir()
    config.option.log_file = str(output / "execution.log")
    config.option.self_contained_html = True


def pytest_report_header(config):
    return [
        f"Target SHA: {os.environ.get('TARGET_SHA', 'unknown')}",
        f"Target root: {os.environ.get('TARGET_ROOT', 'unknown')}",
        f"Diagnostic output: {_output_dir()}",
    ]


def pytest_html_report_title(report):
    report.title = "Diagnóstico Selenium de interacciones UI"


def pytest_html_results_summary(prefix, summary, postfix, session):
    target_sha = escape(os.environ.get("TARGET_SHA", "unknown"))
    prefix.append(f"<p>Commit analizado: {target_sha}</p>")


@pytest.fixture
def driver():
    cache = Path(os.environ.get("SE_CACHE_PATH", _output_dir() / "selenium-cache"))
    cache.mkdir(parents=True, exist_ok=True)
    os.environ["SE_CACHE_PATH"] = str(cache)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,900")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL", "performance": "ALL"})
    browser = webdriver.Chrome(options=options)
    try:
        yield browser
    finally:
        browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if not report.failed:
        return

    browser = item.funcargs.get("driver")
    if browser is None:
        return

    path = _output_dir() / "screenshots" / (
        f"{item.name}_{report.when}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
    )
    try:
        if browser.save_screenshot(str(path)):
            image = base64.b64encode(path.read_bytes()).decode("ascii")
            report.extras = getattr(report, "extras", [])
            report.extras.append(extras.image(image, name=path.name))
            logger.info("Captura diagnóstica guardada: %s", path)
    except Exception as error:
        logger.warning("No se pudo guardar la captura diagnóstica: %s", error)
