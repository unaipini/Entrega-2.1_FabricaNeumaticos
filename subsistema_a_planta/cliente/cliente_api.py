"""
Módulo: cliente/cliente_api.py  —  Subsistema A (Planta)
==========================================================
Arquitectura: Subsistema A = CLIENTE REST
            Subsistema B = SERVIDOR REST

Lógica de resiliencia: POST al Subsistema B; si no hay red,
guarda el neumático en un archivo JSON local (offline-first).
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import requests
from modelos.neumatico import Neumatico

logger = logging.getLogger(__name__)

URL_INSPECCION   = os.getenv("URL_SUBSISTEMA_B", "http://localhost:5000/api/inspeccionar")
ARCHIVO_PENDIENTES = Path(__file__).parent.parent / "data" / "pendientes.json"


class ClienteCalidad:
    """Cliente HTTP con fallback local para comunicación con Subsistema B."""

    def __init__(self, url: str = URL_INSPECCION, timeout: int = 5):
        self.url     = url
        self.timeout = timeout

    def enviar(self, neumatico: Neumatico) -> dict:
        """
        Envía el neumático al Subsistema B.
        Returns dict: {'modo', 'status', 'resultado', 'detalle'}
        """
        try:
            return self._enviar_por_red(neumatico)
        except (requests.ConnectionError, requests.Timeout, requests.RequestException) as err:
            logger.warning("Sin red — guardando localmente. Causa: %s", err)
            self._guardar_local(neumatico)
            return {
                "modo":      "local",
                "status":    None,
                "resultado": "GUARDADO_LOCAL",
                "detalle":   str(err),
            }

    def _enviar_por_red(self, neumatico: Neumatico) -> dict:
        resp = requests.post(self.url, json=neumatico.a_dict(), timeout=self.timeout)
        resultado = "ACEPTADO" if resp.status_code == 200 else "RECHAZADO"
        return {
            "modo":      "red",
            "status":    resp.status_code,
            "resultado": resultado,
            "detalle":   resp.json(),
        }

    def _guardar_local(self, neumatico: Neumatico) -> None:
        ARCHIVO_PENDIENTES.parent.mkdir(parents=True, exist_ok=True)
        registros = []
        if ARCHIVO_PENDIENTES.exists():
            try:
                registros = json.loads(ARCHIVO_PENDIENTES.read_text("utf-8"))
            except json.JSONDecodeError:
                registros = []
        registros.append({
            "timestamp": datetime.utcnow().isoformat(),
            "neumatico": neumatico.a_dict(),
        })
        ARCHIVO_PENDIENTES.write_text(
            json.dumps(registros, ensure_ascii=False, indent=2), "utf-8"
        )
        logger.info("Neumático %s guardado en %s", neumatico.id_neumatico, ARCHIVO_PENDIENTES)
