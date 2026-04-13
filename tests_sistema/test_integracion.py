"""
Tests de Sistema / Integración — Flujo Completo E2E
=====================================================
Levanta el Subsistema B en un hilo separado, luego ejecuta el
Subsistema A para enviarle neumáticos reales por HTTP.
Verifica que el flujo completo de Industria 4.0 funciona
tal como fue diseñado en la arquitectura Cliente-Servidor.

Estrategia:
  1. El fixture `servidor_b` arranca Flask en localhost:5099 (hilo daemon).
  2. Los tests instancian FabricaNeumaticoValido / FabricaNeumaticoDefecto
     y usan ClienteCalidad apuntando al puerto 5099.
  3. Se verifican los códigos HTTP reales y las estadísticas del servidor.

NOTA DE PATH: Subsistema B se inserta DESPUÉS para que tenga mayor prioridad
en sys.path y su modelos/neumatico.py (con desde_dict) no sea opacado por el
del Subsistema A.
"""
import sys
import os
import time
import threading

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── ORDEN CRÍTICO: B al final = mayor prioridad en imports ──────────────────
sys.path.insert(0, os.path.join(BASE, "subsistema_a_planta"))
sys.path.insert(0, os.path.join(BASE, "subsistema_b_calidad"))

import pytest
import requests as http

from flask import Flask
from api.rutas import api_bp, resetear_inspector

from fabrica.fabrica_neumatico import FabricaNeumaticoValido, FabricaNeumaticoDefecto
from cliente.cliente_api import ClienteCalidad

PUERTO_TEST = 5099
URL_BASE    = f"http://localhost:{PUERTO_TEST}/api"


# ═════════════════════════════════════════════════════════════════════════════
#  FIXTURE: Servidor B levantado en hilo de fondo
# ═════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def servidor_b():
    """
    Levanta el Subsistema B (Flask) en un hilo daemon antes de los tests.
    El hilo daemon muere automáticamente con el proceso al finalizar los tests.
    """
    resetear_inspector()
    app = Flask(__name__)
    app.register_blueprint(api_bp)

    hilo = threading.Thread(
        target=lambda: app.run(
            host="127.0.0.1", port=PUERTO_TEST,
            use_reloader=False, debug=False
        ),
        daemon=True,
    )
    hilo.start()

    # Esperar a que el servidor esté listo (máx. 5 seg.)
    for _ in range(50):
        try:
            http.get(f"{URL_BASE}/health", timeout=0.5)
            break
        except (http.exceptions.ConnectionError, http.exceptions.Timeout):
            time.sleep(0.1)
    else:
        pytest.fail("El Subsistema B no respondió en 5 segundos.")

    resetear_inspector()
    yield


@pytest.fixture(autouse=True)
def reset_entre_tests():
    """Resetea los contadores del inspector antes de cada test."""
    resetear_inspector()
    yield


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS DE SISTEMA — Health Check
# ═════════════════════════════════════════════════════════════════════════════

class TestHealthCheck:

    def test_subsistema_b_responde_al_health_check(self, servidor_b):
        """
        Verifica que el Subsistema B (servidor) está activo y responde.
        """
        resp = http.get(f"{URL_BASE}/health", timeout=3)
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS DE SISTEMA — Flujo E2E con neumáticos válidos
# ═════════════════════════════════════════════════════════════════════════════

class TestFlujoNeumaticoValido:

    def test_neumatico_valido_es_aceptado_http_200(self, servidor_b):
        """
        FLUJO COMPLETO — Happy Path:
          Planta (A) → fabrica neumático válido (Factory Method)
          → ClienteCalidad.enviar() → POST HTTP real
          → Subsistema B evalúa con Strategy Pattern
          → HTTP 200 ACEPTADO.
        """
        fabrica = FabricaNeumaticoValido()
        cliente = ClienteCalidad(url=f"{URL_BASE}/inspeccionar")

        neumatico = fabrica.fabricar()
        resultado = cliente.enviar(neumatico)

        assert resultado["modo"]      == "red",       "Debe comunicarse por red"
        assert resultado["status"]    == 200,          "HTTP 200 para neumático válido"
        assert resultado["resultado"] == "ACEPTADO",   "Decisión debe ser ACEPTADO"

    def test_multiples_validos_incrementan_contador_aceptados(self, servidor_b):
        """Los contadores del servidor deben acumular los aceptados correctamente."""
        fabrica = FabricaNeumaticoValido()
        cliente = ClienteCalidad(url=f"{URL_BASE}/inspeccionar")

        for _ in range(3):
            cliente.enviar(fabrica.fabricar())

        stats = http.get(f"{URL_BASE}/estadisticas").json()
        assert stats["inspeccionados"] == 3
        assert stats["aceptados"]      == 3
        assert stats["rechazados"]     == 0

    def test_respuesta_aceptado_contiene_tres_reglas_aprobadas(self, servidor_b):
        """La respuesta debe detallar que las 3 estrategias Strategy aprobaron."""
        fabrica = FabricaNeumaticoValido()
        cliente = ClienteCalidad(url=f"{URL_BASE}/inspeccionar")
        resultado = cliente.enviar(fabrica.fabricar())

        resultados_reglas = resultado["detalle"]["resultados"]
        assert len(resultados_reglas) == 3
        assert all(r["aprobado"] for r in resultados_reglas), \
            "Todas las reglas deben aprobar para un neumático válido"


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS DE SISTEMA — Flujo E2E con neumáticos defectuosos
# ═════════════════════════════════════════════════════════════════════════════

class TestFlujoNeumaticoDefecto:

    def test_neumatico_defecto_es_rechazado_http_406(self, servidor_b):
        """
        FLUJO COMPLETO — Unhappy Path:
          Planta (A) → fabrica neumático defectuoso (Factory Method)
          → ClienteCalidad.enviar() → POST HTTP real
          → Subsistema B detecta fallo con Strategy Pattern
          → HTTP 406 RECHAZADO.
        """
        fabrica = FabricaNeumaticoDefecto()
        cliente = ClienteCalidad(url=f"{URL_BASE}/inspeccionar")

        neumatico = fabrica.fabricar()
        resultado = cliente.enviar(neumatico)

        assert resultado["modo"]      == "red",        "Debe comunicarse por red"
        assert resultado["status"]    == 406,           "HTTP 406 para neumático defectuoso"
        assert resultado["resultado"] == "RECHAZADO",   "Decisión debe ser RECHAZADO"

    def test_multiples_defectuosos_incrementan_contador_rechazados(self, servidor_b):
        """Los contadores del servidor deben acumular los rechazados correctamente."""
        fabrica = FabricaNeumaticoDefecto()
        cliente = ClienteCalidad(url=f"{URL_BASE}/inspeccionar")

        for _ in range(4):
            cliente.enviar(fabrica.fabricar())

        stats = http.get(f"{URL_BASE}/estadisticas").json()
        assert stats["inspeccionados"] == 4
        assert stats["rechazados"]     == 4
        assert stats["aceptados"]      == 0

    def test_respuesta_rechazado_contiene_al_menos_un_fallo(self, servidor_b):
        """La respuesta debe indicar qué estrategia/regla detectó el defecto."""
        fabrica = FabricaNeumaticoDefecto()
        cliente = ClienteCalidad(url=f"{URL_BASE}/inspeccionar")
        resultado = cliente.enviar(fabrica.fabricar())

        resultados_reglas = resultado["detalle"]["resultados"]
        fallos = [r for r in resultados_reglas if not r["aprobado"]]
        assert len(fallos) >= 1, "Debe haber al menos una regla Strategy que falle"
        assert "FALLO" in fallos[0]["detalle"]


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS DE SISTEMA — Estadísticas mixtas
# ═════════════════════════════════════════════════════════════════════════════

class TestEstadisticasMixtas:

    def test_contadores_reflejan_mezcla_correcta(self, servidor_b):
        """2 válidos + 3 defectuosos = 5 inspeccionados, 2 aceptados, 3 rechazados."""
        fab_valido  = FabricaNeumaticoValido()
        fab_defecto = FabricaNeumaticoDefecto()
        cliente     = ClienteCalidad(url=f"{URL_BASE}/inspeccionar")

        for _ in range(2): cliente.enviar(fab_valido.fabricar())
        for _ in range(3): cliente.enviar(fab_defecto.fabricar())

        stats = http.get(f"{URL_BASE}/estadisticas").json()
        assert stats["inspeccionados"] == 5
        assert stats["aceptados"]      == 2
        assert stats["rechazados"]     == 3

    def test_respuesta_post_incluye_estadisticas_actualizadas(self, servidor_b):
        """La respuesta del POST /inspeccionar ya incluye los contadores actualizados."""
        fabrica = FabricaNeumaticoValido()
        cliente = ClienteCalidad(url=f"{URL_BASE}/inspeccionar")
        resultado = cliente.enviar(fabrica.fabricar())

        assert resultado["modo"] == "red"
        stats = resultado["detalle"]["estadisticas"]
        assert stats["inspeccionados"] >= 1

    def test_endpoint_estadisticas_get_siempre_responde_200(self, servidor_b):
        """GET /api/estadisticas siempre debe responder HTTP 200."""
        resp = http.get(f"{URL_BASE}/estadisticas")
        assert resp.status_code == 200
        data = resp.json()
        assert "inspeccionados" in data
        assert "aceptados"      in data
        assert "rechazados"     in data
