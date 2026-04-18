"""
Tests de Componente — Subsistema A (Planta)
============================================
Objetivo: Probar ClienteCalidad de forma aislada, mockeando la capa HTTP
para verificar que el cliente:
  · Hace el POST correcto al endpoint del Subsistema B.
  · Interpreta HTTP 200 como ACEPTADO y HTTP 406 como RECHAZADO.
  · Ante un error de red, persiste el neumático localmente.

Se usa unittest.mock para reemplazar 'requests.post' sin levantar un servidor real.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import math

from modelos.neumatico import Neumatico
from cliente.cliente_api import ClienteCalidad
import requests

# ─── Fixture de neumático de prueba ──────────────────────────────────────────
@pytest.fixture
def neumatico_valido():
    return Neumatico(
        id_neumatico="comp-test-001",
        radio_pulgadas=16.0,
        peso_kg=9.5,
        profundidad_huella_mm=3.2,
    )

@pytest.fixture
def cliente(tmp_path, monkeypatch):
    """Cliente con archivo local redirigido a un directorio temporal."""
    import cliente.cliente_api as mod_cliente
    archivo_temp = tmp_path / "data" / "pendientes.json"
    monkeypatch.setattr(mod_cliente, "ARCHIVO_PENDIENTES", archivo_temp)
    return ClienteCalidad(url="http://mock-servidor-b/api/inspeccionar")


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS DE COMPONENTE — Respuesta HTTP 200 (ACEPTADO)
# ═════════════════════════════════════════════════════════════════════════════

class TestClienteCalidadRed:

    def test_envia_post_al_endpoint_correcto(self, cliente, neumatico_valido):
        """Verifica que el cliente llama a requests.post con la URL correcta."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"decision": "ACEPTADO"}

        with patch("requests.post", return_value=mock_resp) as mock_post:
            cliente.enviar(neumatico_valido)
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert args[0] == "http://mock-servidor-b/api/inspeccionar"

    def test_envia_payload_json_correcto(self, cliente, neumatico_valido):
        """El payload enviado debe contener todos los campos del neumático."""
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {"decision": "ACEPTADO"}

        with patch("requests.post", return_value=mock_resp) as mock_post:
            cliente.enviar(neumatico_valido)
            _, kwargs = mock_post.call_args
            payload = kwargs["json"]

            assert payload["id_neumatico"] == "comp-test-001"
            
            assert math.isclose(payload["radio_pulgadas"], 16.0)
            assert math.isclose(payload["peso_kg"], 9.5)
            assert math.isclose(payload["profundidad_huella_mm"], 3.2)

    def test_http_200_devuelve_resultado_aceptado(self, cliente, neumatico_valido):
        """HTTP 200 del servidor debe mapearse a resultado ACEPTADO."""
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {"decision": "ACEPTADO"}

        with patch("requests.post", return_value=mock_resp):
            resultado = cliente.enviar(neumatico_valido)

        assert resultado["modo"]      == "red"
        assert resultado["status"]    == 200
        assert resultado["resultado"] == "ACEPTADO"

    def test_http_406_devuelve_resultado_rechazado(self, cliente, neumatico_valido):
        """HTTP 406 del servidor debe mapearse a resultado RECHAZADO."""
        mock_resp = MagicMock(status_code=406)
        mock_resp.json.return_value = {"decision": "RECHAZADO"}

        with patch("requests.post", return_value=mock_resp):
            resultado = cliente.enviar(neumatico_valido)

        assert resultado["modo"]      == "red"
        assert resultado["status"]    == 406
        assert resultado["resultado"] == "RECHAZADO"


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS DE COMPONENTE — Modo sin red (fallback local)
# ═════════════════════════════════════════════════════════════════════════════

class TestClienteCalidadFallbackLocal:

    def test_error_conexion_devuelve_guardado_local(self, cliente, neumatico_valido):
        """Ante ConnectionError, el resultado debe indicar modo local."""
        with patch("requests.post", side_effect=requests.ConnectionError("sin red")):
            resultado = cliente.enviar(neumatico_valido)

        assert resultado["modo"]      == "local"
        assert resultado["status"]    is None
        assert resultado["resultado"] == "GUARDADO_LOCAL"

    def test_timeout_devuelve_guardado_local(self, cliente, neumatico_valido):
        """Ante Timeout, el resultado debe indicar modo local."""
        with patch("requests.post", side_effect=requests.Timeout("timeout")):
            resultado = cliente.enviar(neumatico_valido)

        assert resultado["resultado"] == "GUARDADO_LOCAL"

    def test_crea_archivo_json_local_cuando_no_hay_red(
        self, cliente, neumatico_valido, tmp_path, monkeypatch
    ):
        """Verifica que se crea el archivo JSON local con el neumático."""
        import cliente.cliente_api as mod_cliente
        archivo = tmp_path / "data" / "pendientes.json"
        monkeypatch.setattr(mod_cliente, "ARCHIVO_PENDIENTES", archivo)

        with patch("requests.post", side_effect=requests.ConnectionError()):
            cliente.enviar(neumatico_valido)

        assert archivo.exists(), "El archivo JSON local no fue creado"
        registros = json.loads(archivo.read_text("utf-8"))
        assert len(registros) == 1
        assert registros[0]["neumatico"]["id_neumatico"] == "comp-test-001"

    def test_acumula_registros_en_archivo_local(
        self, cliente, neumatico_valido, tmp_path, monkeypatch
    ):
        """Múltiples envíos fallidos deben acumular registros en el JSON."""
        import cliente.cliente_api as mod_cliente
        archivo = tmp_path / "data" / "pendientes.json"
        monkeypatch.setattr(mod_cliente, "ARCHIVO_PENDIENTES", archivo)

        with patch("requests.post", side_effect=requests.ConnectionError()):
            for _ in range(3):
                cliente.enviar(neumatico_valido)

        registros = json.loads(archivo.read_text("utf-8"))
        assert len(registros) == 3
