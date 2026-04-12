"""
Tests de Componente — Subsistema B (API REST)
==============================================
Prueba los endpoints de la API usando el test client de Flask,
sin necesidad de levantar un servidor real (prueba interna de componente).

Cubre:
  · POST /api/inspeccionar → neumático válido (200)
  · POST /api/inspeccionar → neumático inválido (406)
  · POST /api/inspeccionar → payload malformado (400)
  · POST /api/inspeccionar → campos faltantes (400)
  · GET  /api/estadisticas → contadores correctos
  · GET  /api/health       → health-check operativo
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from flask import Flask

from api.rutas import api_bp, resetear_inspector
from servicio.inspector import InspectorCalidad

# ─── Fixture de la app de test ────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_inspector():
    """Resetea el inspector antes de cada test para aislar contadores."""
    resetear_inspector()
    yield
    resetear_inspector()

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# ─── Payloads de prueba ───────────────────────────────────────────────────────

NEUMATICO_VALIDO = {
    "id_neumatico":          "api-test-valido-001",
    "radio_pulgadas":        16.0,
    "peso_kg":               9.5,
    "profundidad_huella_mm": 3.2,
}

NEUMATICO_RADIO_FUERA = {
    "id_neumatico":          "api-test-radio-001",
    "radio_pulgadas":        17.5,    # fuera de [15.8, 16.2]
    "peso_kg":               9.5,
    "profundidad_huella_mm": 3.2,
}

NEUMATICO_PESO_FUERA = {
    "id_neumatico":          "api-test-peso-001",
    "radio_pulgadas":        16.0,
    "peso_kg":               11.0,   # fuera de [9.0, 10.0]
    "profundidad_huella_mm": 3.2,
}

NEUMATICO_HUELLA_FUERA = {
    "id_neumatico":          "api-test-huella-001",
    "radio_pulgadas":        16.0,
    "peso_kg":               9.5,
    "profundidad_huella_mm": 1.0,    # < 1.6 mm
}


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS DE COMPONENTE — POST /api/inspeccionar
# ═════════════════════════════════════════════════════════════════════════════

class TestEndpointInspeccionar:

    def test_neumatico_valido_retorna_200(self, client):
        resp = client.post("/api/inspeccionar", json=NEUMATICO_VALIDO)
        assert resp.status_code == 200

    def test_neumatico_valido_decision_aceptado(self, client):
        resp = client.post("/api/inspeccionar", json=NEUMATICO_VALIDO)
        assert resp.get_json()["decision"] == "ACEPTADO"

    def test_neumatico_radio_invalido_retorna_406(self, client):
        resp = client.post("/api/inspeccionar", json=NEUMATICO_RADIO_FUERA)
        assert resp.status_code == 406

    def test_neumatico_radio_invalido_decision_rechazado(self, client):
        resp = client.post("/api/inspeccionar", json=NEUMATICO_RADIO_FUERA)
        assert resp.get_json()["decision"] == "RECHAZADO"

    def test_neumatico_peso_invalido_retorna_406(self, client):
        resp = client.post("/api/inspeccionar", json=NEUMATICO_PESO_FUERA)
        assert resp.status_code == 406

    def test_neumatico_huella_invalida_retorna_406(self, client):
        resp = client.post("/api/inspeccionar", json=NEUMATICO_HUELLA_FUERA)
        assert resp.status_code == 406

    def test_payload_vacio_retorna_400(self, client):
        resp = client.post("/api/inspeccionar", data="no-json",
                           content_type="text/plain")
        assert resp.status_code == 400

    def test_campo_faltante_retorna_400(self, client):
        incompleto = {k: v for k, v in NEUMATICO_VALIDO.items()
                      if k != "peso_kg"}
        resp = client.post("/api/inspeccionar", json=incompleto)
        assert resp.status_code == 400

    def test_respuesta_contiene_id_neumatico(self, client):
        resp = client.post("/api/inspeccionar", json=NEUMATICO_VALIDO)
        assert resp.get_json()["id_neumatico"] == "api-test-valido-001"

    def test_respuesta_contiene_resultados_por_regla(self, client):
        resp = client.post("/api/inspeccionar", json=NEUMATICO_VALIDO)
        resultados = resp.get_json()["resultados"]
        nombres = {r["regla"] for r in resultados}
        assert "ReglaRadio"  in nombres
        assert "ReglaPeso"   in nombres
        assert "ReglaHuella" in nombres

    def test_respuesta_incluye_estadisticas(self, client):
        resp = client.post("/api/inspeccionar", json=NEUMATICO_VALIDO)
        assert "estadisticas" in resp.get_json()


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS DE COMPONENTE — GET /api/estadisticas
# ═════════════════════════════════════════════════════════════════════════════

class TestEndpointEstadisticas:

    def test_estadisticas_iniciales_son_cero(self, client):
        resp = client.get("/api/estadisticas")
        data = resp.get_json()
        assert data["inspeccionados"] == 0
        assert data["aceptados"]      == 0
        assert data["rechazados"]     == 0

    def test_estadisticas_se_acumulan_correctamente(self, client):
        client.post("/api/inspeccionar", json=NEUMATICO_VALIDO)      # +1 aceptado
        client.post("/api/inspeccionar", json=NEUMATICO_RADIO_FUERA) # +1 rechazado
        resp = client.get("/api/estadisticas")
        data = resp.get_json()
        assert data["inspeccionados"] == 2
        assert data["aceptados"]      == 1
        assert data["rechazados"]     == 1


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS DE COMPONENTE — GET /api/health
# ═════════════════════════════════════════════════════════════════════════════

class TestEndpointHealth:

    def test_health_retorna_200(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_health_retorna_status_ok(self, client):
        resp = client.get("/api/health")
        assert resp.get_json()["status"] == "ok"
