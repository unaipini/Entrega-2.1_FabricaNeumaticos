"""
Módulo: api/rutas.py  —  Subsistema B (Calidad)
=================================================
Endpoints REST del Subsistema B (Servidor).

Endpoints:
    POST /api/inspeccionar   → HTTP 200 (Aceptado) | HTTP 406 (Rechazado) | HTTP 400
    GET  /api/estadisticas   → Contadores en memoria.
    GET  /api/health         → Health-check para CI/CD.
"""
import logging
from flask import Blueprint, request, jsonify

from modelos.neumatico import Neumatico
from servicio.inspector import InspectorCalidad

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Instancia única del inspector (singleton de sesión)
_inspector = InspectorCalidad()


@api_bp.route("/inspeccionar", methods=["POST"])
def inspeccionar():
    """
    POST /api/inspeccionar
    ----------------------
    Evalúa un neumático recibido por JSON contra las reglas de calidad
    (Strategy Pattern). Devuelve HTTP 200 (Aceptado) o HTTP 406 (Rechazado).
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Payload JSON requerido"}), 400

    campos_requeridos = ["id_neumatico", "radio_pulgadas", "peso_kg", "profundidad_huella_mm"]
    faltantes = [c for c in campos_requeridos if c not in datos]
    if faltantes:
        return jsonify({"error": f"Campos faltantes: {faltantes}"}), 400

    try:
        # Construcción directa — evita conflictos de cache de módulos
        # entre test suites que combinan ambos subsistemas.
        neumatico = Neumatico(
            id_neumatico=str(datos["id_neumatico"]),
            radio_pulgadas=float(datos["radio_pulgadas"]),
            peso_kg=float(datos["peso_kg"]),
            profundidad_huella_mm=float(datos["profundidad_huella_mm"]),
        )
    except (KeyError, ValueError, TypeError) as exc:
        return jsonify({"error": f"Datos inválidos: {exc}"}), 400

    # ── Ejecutar las estrategias de calidad (Strategy Pattern) ──
    aprobado, resultados = _inspector.inspeccionar(neumatico)

    respuesta = {
        "id_neumatico": neumatico.id_neumatico,
        "decision":     "ACEPTADO" if aprobado else "RECHAZADO",
        "resultados":   resultados,
        "estadisticas": _inspector.estadisticas(),
    }
    return jsonify(respuesta), (200 if aprobado else 406)


@api_bp.route("/estadisticas", methods=["GET"])
def estadisticas():
    """GET /api/estadisticas — Devuelve contadores acumulados en memoria."""
    return jsonify(_inspector.estadisticas()), 200


@api_bp.route("/health", methods=["GET"])
def health():
    """GET /api/health — Health-check para CI/CD y monitoreo."""
    return jsonify({"status": "ok", "subsistema": "B-Calidad"}), 200


def obtener_inspector() -> InspectorCalidad:
    """Expone el inspector para inyección en tests de componente."""
    return _inspector


def resetear_inspector(nuevo_inspector: InspectorCalidad = None) -> None:
    """Reemplaza el inspector; útil para resetear contadores en tests."""
    global _inspector
    _inspector = nuevo_inspector or InspectorCalidad()
