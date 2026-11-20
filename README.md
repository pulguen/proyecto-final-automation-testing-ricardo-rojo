# Trabajo Final Integrador - Automation Testing SauceDemo

**Autor:** Ricardo Rojo

El proyecto evoluciona desde la pre-entrega. Esta etapa centraliza la configuración y separa las evidencias por ejecución, conservando los ocho casos UI originales.

## Descripción

Suite automatizada sobre [SauceDemo](https://www.saucedemo.com/), desarrollada como pre-entrega del curso de Automation Testing. Aplica conceptos trabajados hasta las clases 6, 7 y 8: login, catálogo, navegación al detalle y carrito, con casos positivos y negativos.

El alcance actual incluye ocho pruebas funcionales independientes. No incluye checkout, usuarios especiales, pruebas entre distintos navegadores ni CI/CD.

## Objetivos

- Aplicar Selenium WebDriver para interactuar con una aplicación web.
- Localizar elementos mediante selectores estables y legibles.
- Utilizar Pytest, fixtures y validaciones con mensajes claros.
- Sincronizar las acciones mediante esperas explícitas.
- Implementar Page Object Model (POM).
- Crear pruebas independientes con un navegador nuevo por test.
- Generar evidencias mediante reporte HTML, capturas de fallos y logs.

## Tecnologías utilizadas

- Python 3.12, versión utilizada para validar esta entrega.
- Selenium WebDriver y Selenium Manager para resolver ChromeDriver.
- Pytest.
- pytest-html.
- Google Chrome.
- `logging`, `pathlib`, `datetime` y `re` de la biblioteca estándar de Python.
- Git para el control de versiones local; GitHub como destino previsto de la entrega.

Las tres dependencias directas están en [requirements.txt](./requirements.txt). Se mantienen los rangos de versiones que ya funcionaban. No se agregaron dependencias para logs ni capturas.

## Estructura del proyecto

El proyecto actual es `proyecto-final-automation-testing-ricardo-rojo`. El remoto `origin` apunta al [repositorio del trabajo final](https://github.com/pulguen/proyecto-final-automation-testing-ricardo-rojo) y `upstream` conserva la referencia a la pre-entrega.

```text
proyecto-final-automation-testing-ricardo-rojo/
├── pages/
│   ├── __init__.py
│   ├── login_page.py
│   ├── inventory_page.py
│   └── cart_page.py
├── tests/
│   ├── __init__.py
│   ├── test_login.py
│   ├── test_inventory.py
│   └── test_cart.py
├── utils/
│   ├── __init__.py
│   ├── config.py
│   └── helpers.py
├── reports/
│   ├── screenshots/
│   │   ├── .gitkeep
│   │   ├── test_agregar_producto_carrito_call_20261008_081732_409094.png
│   │   ├── test_eliminar_producto_carrito_call_20261008_083013_229910.png
│   │   └── test_evidencia_fallo_controlado_call_20261008_081330_874074.png
│   ├── logs/
│   │   ├── .gitkeep
│   │   └── execution.log
│   ├── reporte.html
│   └── runs/                 # ejecuciones nuevas, ignoradas por Git
├── conftest.py
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

El árbol muestra los archivos fuente y las evidencias. También existen carpetas locales de entorno y caché, como `venv`, `.tools`, `.pytest_cache` y `__pycache__`, excluidas del repositorio.

Los paquetes Python contienen archivos llamados `__init__.py`, con dos guiones bajos a cada lado. Las ejecuciones diagnósticas repetidas se resumen más abajo; sus XML, CSV y logs redundantes no forman parte de la entrega.

- [pages/](./pages/): locators, acciones y lecturas de cada página. Las acciones del detalle permanecen en `InventoryPage` para mantener simple la estructura.
- [tests/](./tests/): preparación específica, acciones y validaciones de los ocho casos.
- [utils/](./utils/): función auxiliar para guardar capturas de forma segura.
- [reports/](./reports/): reporte HTML, logs e imágenes de evidencia.
- [conftest.py](./conftest.py): fixtures compartidas y hooks de Pytest para registrar resultados y capturar fallos.
- [pytest.ini](./pytest.ini): descubrimiento de tests, ruta temporal local y configuración de logging.

## Casos de prueba

| ID | Caso | Tipo | Cobertura |
| --- | --- | --- | --- |
| TC-01 | Login exitoso | Positivo | Mínimo obligatorio |
| TC-02 | Login con credenciales inválidas | Negativo | Adicional |
| TC-03 | Visualización del catálogo | Positivo | Mínimo obligatorio |
| TC-04 | Elementos principales de interfaz | Positivo | Mínimo obligatorio |
| TC-05 | Detalle del primer producto | Positivo | Adicional |
| TC-06 | Agregar producto al carrito | Positivo | Mínimo obligatorio |
| TC-07 | Agregar dos productos | Positivo | Adicional |
| TC-08 | Eliminar producto del carrito | Positivo | Adicional |

TC-01 verifica la URL del inventario y los textos `Products` y `Swag Labs`. TC-03 valida el título de la pestaña y muestra el nombre y el precio del primer producto. TC-06 espera explícitamente el badge y compara el producto agregado con el del carrito. TC-07 verifica dos nombres sin exigir un orden; TC-08 comprueba que desaparezcan el producto y el badge.

## Instalación

Se necesita Python, Google Chrome instalado y conexión a Internet para acceder a SauceDemo. En la primera ejecución Selenium Manager puede descargar el ChromeDriver compatible. Su caché queda dentro de `.tools/selenium`.

Ejecutar los comandos desde la raíz del proyecto:

```powershell
python -m venv venv
```

Activar el entorno en PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

En CMD, el equivalente es:

```bat
venv\Scripts\activate
```

Instalar las dependencias con el Python del entorno activo:

```powershell
python -m pip install -r requirements.txt
```

Si el entorno no está activado, después de crearlo e instalar las dependencias puede ejecutarse directamente:

```powershell
.\venv\Scripts\python.exe -m pytest -v --headless
```

En otro equipo se puede crear un entorno nuevo siguiendo los pasos anteriores; no es necesario copiar el entorno local ni instalar `uv` para ejecutar la suite.

## Ejecución

Todos los tests, con Chrome visible por defecto:

```powershell
python -m pytest -v
```

Solo UI, sin ventana y mostrando la salida de consola:

```powershell
python -m pytest -v -s -m ui --headless
```

Ejecutar un archivo o un caso individual:

```powershell
python -m pytest tests/test_login.py -v --headless
python -m pytest tests/test_cart.py::test_agregar_dos_productos -v --headless
```

Cada ejecución genera automáticamente un HTML autocontenido, un log y una carpeta de screenshots en un directorio único. Pytest muestra sus rutas en la cabecera. Ya no es necesario indicar `--html`.

Las opciones `--html` y `--log-file` permiten nombres personalizados, pero se rechaza cualquier archivo de salida que ya exista. Esto protege también el HTML y el log históricos de la pre-entrega.

## Configuración del framework

[utils/config.py](./utils/config.py) utiliza solamente la biblioteca estándar. Las variables se leen del entorno; no se necesita un archivo `.env` ni una dependencia adicional.

| Variable | Valor por defecto | Uso |
| --- | --- | --- |
| `BASE_URL` | `https://www.saucedemo.com/` | URL de entrada a SauceDemo |
| `SELENIUM_TIMEOUT` | `10` | Segundos de espera explícita en los tres Page Objects |
| `EVIDENCE_DIR` | `reports/runs` | Directorio base de las nuevas ejecuciones |

La URL debe ser HTTP/HTTPS y el timeout debe ser positivo y finito. Los valores inválidos detienen la ejecución con un mensaje claro, sin sustituirlos silenciosamente.

Ejemplo en PowerShell, limitado a la terminal actual:

```powershell
$env:BASE_URL = "https://www.saucedemo.com/"
$env:SELENIUM_TIMEOUT = "10"
$env:EVIDENCE_DIR = "reports/runs/entorno"
python -m pytest -v -m ui --headless
```

`--output-dir` tiene prioridad sobre `EVIDENCE_DIR`. Se aceptan rutas absolutas; las relativas se interpretan desde la raíz del proyecto:

```powershell
python -m pytest -v -m ui --headless --output-dir reports/runs/otra-ubicacion
```

Dentro del directorio base se crea una subcarpeta con fecha, hora y un sufijo único. Contiene `reporte.html`, `logs/execution.log` y `screenshots/`. No se reutiliza una carpeta de ejecución anterior. Las salidas bajo `reports/runs/` están ignoradas por Git; al elegir otro destino dentro del repositorio se deben revisar sus exclusiones antes de versionar.

Los markers `ui` y `api` están registrados con `--strict-markers`. Los ocho tests llevan `pytest.mark.ui` a nivel de módulo, sin cambios en sus asserts. `api` está reservado; todavía no hay pruebas API. Se conserva Chrome visible por defecto y `--headless` para ejecutar sin ventana.

## Independencia de las pruebas

La fixture `driver` tiene alcance por función: crea una sesión nueva de Chrome para cada test y cierra el navegador mediante `finally`. La fixture `inventory_page` reutiliza `LoginPage` para iniciar sesión y esperar el inventario. Ambas están definidas una sola vez en [conftest.py](./conftest.py).

Cada caso prepara sus propios datos. Ningún test depende de que otro haya agregado productos o iniciado sesión anteriormente.

## Evidencias

Las evidencias versionadas de la pre-entrega se mantienen como históricas y no se sobrescriben:

- [Reporte HTML histórico](./reports/reporte.html): resultado de la pre-entrega.
- [Capturas históricas](./reports/screenshots/): prueba controlada e incidencias documentadas.
- [Log histórico](./reports/logs/execution.log): registro de la ejecución final de la pre-entrega.

Las nuevas ejecuciones usan el directorio único descrito arriba. Su log mantiene el formato `fecha - nivel - mensaje`, y los screenshots automáticos se guardan en el subdirectorio `screenshots` de esa misma ejecución. Todavía no se incrustan ni se enlazan las capturas dentro del HTML.

El hook `pytest_runtest_makereport` recibe el resultado de las fases de preparación, ejecución y cierre. Cuando detecta un fallo, llama a la función de [helpers.py](./utils/helpers.py), que verifica la sesión y las ventanas, crea la carpeta si hace falta y guarda la captura. El nombre incluye test, fase y fecha/hora con microsegundos para evitar sobrescrituras.

Si Chrome no llegó a abrirse o ya se cerró, puede no haber captura. Si falla el guardado, se escribe una advertencia en el log y se conserva el fallo original del test. Los asserts y Page Objects no contienen llamadas manuales para guardar screenshots.

Se conserva una [captura de un fallo controlado](./reports/screenshots/test_evidencia_fallo_controlado_call_20261008_081330_874074.png) exclusivamente para demostrar que el mecanismo funciona. Se produjo con un test temporal que comparaba `Products` con un texto incorrecto a propósito. El test temporal fue eliminado; esta imagen **no representa un fallo de los ocho casos funcionales**. El reporte y el log finales corresponden a una ejecución posterior de la suite completa.

La selección publicada contiene siete archivos de evidencia: el HTML final, el log final, tres capturas (una controlada y dos históricas) y dos `.gitkeep`. Se retiraron 71 archivos redundantes de diagnóstico e incidencias y se conservaron únicamente como archivo local ignorado, fuera del historial de la rama a publicar.

Para preparar el log final se sustituyó la ruta absoluta del proyecto por `.` en la línea de inicio de ejecución. No se alteraron fechas, resultados ni acciones. El HTML final y las capturas se conservaron sin modificaciones. Si se regeneran evidencias, corresponde revisar nuevamente sus metadatos antes de publicarlas.

[.gitignore](./.gitignore) excluye entornos, cachés y configuraciones locales de IDE; permite incluir el reporte, los logs y las capturas como parte de la entrega.

## Estrategia de localización

Se prioriza ID único, luego NAME cuando resulte apropiado, CSS corto y estable, y CLASS_NAME cuando una clase identifica claramente el elemento. XPath relativo se reserva para una necesidad que las alternativas anteriores no resuelvan bien; se evitan XPath absolutos.

En esta suite se usan ID, CSS basado en atributos `data-test` y CLASS_NAME para la marca. No se forzó el uso de NAME ni XPath solo para demostrar otra estrategia. Los botones de agregar y eliminar se buscan dentro del producto seleccionado mediante prefijos de ID estables. Elegir el primer o segundo producto responde al caso de prueba; no depende de `nth-child` ni de una estructura DOM larga.

## Esperas

Se utilizan `WebDriverWait` y `expected_conditions` para visibilidad, clics, navegación y desaparición de elementos. Para el badge se espera primero su visibilidad y luego la igualdad exacta con el valor esperado mediante una condición sencilla. No se utiliza `time.sleep()` para sincronizar las pruebas.

Al agregar un producto, se obtiene el ID de su botón, se vuelve a localizar mediante `element_to_be_clickable` y se hace un único clic normal. Después se espera la visibilidad del botón `Remove` correspondiente como confirmación de que la aplicación procesó la acción. Solo entonces continúa la espera del badge. Por defecto se conservan los 10 segundos de cada espera, configurables mediante `SELENIUM_TIMEOUT`; no hay clics repetidos ni clics por JavaScript.

Al vaciar el carrito, SauceDemo elimina el badge del DOM. Por eso se espera su ausencia y no el texto `0`.

## Page Object Model

Los locators, las acciones y las lecturas de las páginas están en [pages/](./pages/). Las validaciones con `assert` permanecen en [tests/](./tests/). Esta separación permite ajustar un selector sin reescribir los casos y mantiene cada test centrado en el comportamiento que verifica.

## Resultado actual

Las dos validaciones completas posteriores al ajuste de sincronización, una con salida de consola y otra con reporte HTML autocontenido, terminaron con:

```text
8 passed
```

El [reporte histórico](./reports/reporte.html) y el [log histórico](./reports/logs/execution.log) corresponden a la última suite completa conservada de la pre-entrega. Las incidencias anteriores se conservan por separado. No se modificaron los ocho tests funcionales ni sus asserts.

La duración puede variar según el equipo y la conexión. Con `-s`, TC-03 muestra:

```text
Primer producto: Sauce Labs Backpack
Precio: $29.99
```

El nombre y el precio se leen del sitio durante la ejecución; no están fijados en el test.

### Diagnóstico y muestra de estabilidad del carrito

Antes del ajuste se ejecutaron cinco rondas con TC-06 y TC-08: diez pruebas aprobadas. La instrumentación temporal registró que los eventos del mouse llegaron al botón correcto y que, tras el clic exitoso, el botón original fue reemplazado: quedó stale mientras aparecían `Remove` y el badge `1`. Ese reemplazo se observó en pruebas aprobadas; no demuestra que haya causado los fallos históricos.

No se reprodujo un timeout durante la muestra instrumentada. Por ello no se pudo determinar si en los eventos históricos hubo un clic sin efecto, un retraso del DOM o algún otro problema. La instrumentación también agrega tiempo de observación: sus resultados no permiten atribuir una causa por descarte.

La mejora consiste en relocalizar el botón por ID inmediatamente antes del clic y confirmar `Remove` antes del badge. La sonda JavaScript de observación se retiró. Permanecen registros breves de URL, producto, texto, visibilidad y habilitación del botón antes del clic; y de Add, Remove, badge y referencia original después. Si hay un error de WebDriver, se registra el estado y se propaga la excepción, sin continuar el test.

Después del ajuste se ejecutó una muestra de tamaño fijado de antemano, sin plugins de repetición ni reintentos hasta obtener éxito:

| Grupo | Ejecuciones | Aprobadas | Fallidas |
| --- | --- | --- | --- |
| TC-06 individual | 10 | 10 | 0 |
| TC-08 individual | 10 | 10 | 0 |
| Archivo de carrito, tres tests por ronda | 5 rondas | 15 tests | 0 |
| Suite completa con consola | 1 ronda | 8 tests | 0 |
| Suite completa con HTML | 1 ronda | 8 tests | 0 |

Los conteos se verificaron contra los XML de Pytest antes de simplificar las evidencias. TC-06 y TC-08 acumularon 15 ejecuciones posteriores cada uno al incluir las cinco rondas del archivo completo. Los archivos detallados de cada ronda no se publican para evitar duplicaciones y metadatos locales innecesarios; esta tabla conserva el resumen de la validación realizada.

La muestra aporta confianza en la sincronización actual, pero no demuestra una solución causal de las incidencias históricas: **la causa original sigue sin confirmarse**.

### Incidencia histórica de TC-06

- **Comportamiento observado:** una ejecución intermedia terminó con `1 failed, 7 passed`. TC-06 agotó los 10 segundos de espera del badge después del clic para agregar el primer producto. La captura muestra el carrito vacío y el botón todavía en `Add to cart`.
- **Resultado esperado:** aparece el badge con valor `1`; al abrir el carrito, figura el mismo producto seleccionado en el catálogo.
- **Evidencia conservada en la entrega:** [captura automática histórica de TC-06](./reports/screenshots/test_agregar_producto_carrito_call_20261008_081732_409094.png). El reporte intermedio y su log se retiraron de la versión publicada para reducir redundancia; sus originales permanecen en el archivo local ignorado.
- **Intento de reproducción anterior al ajuste:** TC-06 pasó individualmente y después la suite completa pasó dos veces. No se modificaron asserts, selectores ni esperas para obtener esos resultados. La muestra posterior al ajuste se detalla arriba.
- **Estado actual:** no reproducible en los intentos posteriores; pendiente de causa confirmada. No se atribuye a Selenium, al sitio ni a la conexión sin evidencia suficiente. Se conserva como observación QA histórica, no como un fallo actual confirmado ni como una corrección demostrada.

Esta incidencia es distinta de la prueba deliberada del mecanismo de capturas. El reporte versionado corresponde a la validación histórica de la pre-entrega; los nuevos reportes se guardan por ejecución.

### Incidencia histórica de TC-08

- **Comportamiento observado:** en una validación anterior con reporte HTML, TC-08 agotó los 10 segundos esperando el badge después de agregar un producto, antes de abrir el carrito o eliminarlo. La ejecución terminó con `1 failed, 7 passed`; TC-06 pasó en esa misma corrida.
- **Resultado esperado:** el producto pasa a `Remove`, aparece el badge `1` y el test puede continuar con su validación de eliminación.
- **Evidencia conservada en la entrega:** [captura automática histórica de TC-08](./reports/screenshots/test_eliminar_producto_carrito_call_20261008_083013_229910.png). La imagen muestra el carrito vacío y el botón en `Add to cart`. El reporte anterior y su log se retiraron de la versión publicada; sus originales permanecen en el archivo local ignorado.
- **Intentos posteriores:** cinco ejecuciones instrumentadas antes del ajuste, diez individuales después, cinco dentro de las rondas de carrito y dos suites completas, todas aprobadas.
- **Estado:** no reproducido durante este diagnóstico; causa sin confirmar. Comparte el punto de espera con TC-06, pero no está demostrado que ambos eventos tengan la misma causa.
