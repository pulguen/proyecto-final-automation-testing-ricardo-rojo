"""Utilidades para guardar evidencias sin alterar el resultado de los tests."""

from datetime import datetime
import logging
from pathlib import Path
import re


logger = logging.getLogger(__name__)


def save_failure_screenshot(driver, test_name, phase):
    """Guardar una captura si Chrome sigue disponible; un error solo se registra."""
    if driver is None:
        logger.warning("Sin captura de %s: no hay una instancia de driver", test_name)
        return None

    try:
        if not driver.session_id or not driver.window_handles:
            logger.warning("Sin captura de %s: no hay una ventana activa", test_name)
            return None

        folder = Path(__file__).resolve().parents[1] / "reports" / "screenshots"
        folder.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", test_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = folder / f"{safe_name}_{phase}_{timestamp}.png"

        if not driver.save_screenshot(str(path)):
            logger.warning("No se pudo guardar la captura de %s", test_name)
            return None

        logger.info("Captura de fallo guardada: %s", path)
        return path
    except Exception as error:
        # La evidencia es secundaria: se conserva el fallo original de Pytest.
        logger.warning("No se pudo capturar %s: %s", test_name, error)
        return None
