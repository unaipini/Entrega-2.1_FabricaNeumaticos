"""
Módulo: servicio/inspector.py  —  Subsistema B (Calidad)
==========================================================
PATRÓN STRATEGY — Contexto (Context)
--------------------------------------
InspectorCalidad es el "Contexto" del patrón Strategy.
Mantiene una referencia a la lista de estrategias (ReglaCalidad)
y las ejecuta secuencialmente sobre cada neumático recibido.
Además, lleva los contadores en memoria (inspeccionados,
aceptados, rechazados) tal como exigen las reglas de negocio.
"""
import logging
from typing import List

from estrategias.regla_calidad import ReglaCalidad
from estrategias.reglas_concretas import ReglaRadio, ReglaPeso, ReglaHuella
from modelos.neumatico import Neumatico

logger = logging.getLogger(__name__)


class InspectorCalidad:
    """
    [STRATEGY — Contexto]
    Ejecuta la lista de estrategias de calidad sobre un neumático
    y gestiona los contadores globales de la sesión.

    Uso típico:
        inspector = InspectorCalidad()
        aprobado, detalle = inspector.inspeccionar(neumatico)
    """

    def __init__(self, reglas: List[ReglaCalidad] = None):
        # Si no se inyectan reglas, usa el conjunto estándar de producción.
        # La inyección permite sustituir estrategias en tests (DIP + Strategy).
        self._reglas: List[ReglaCalidad] = reglas or [
            ReglaRadio(),    # ← Estrategia concreta 1
            ReglaPeso(),     # ← Estrategia concreta 2
            ReglaHuella(),   # ← Estrategia concreta 3
        ]
        # ── Contadores en memoria (requisito de negocio) ──────
        self.total_inspeccionados: int = 0
        self.total_aceptados:     int = 0
        self.total_rechazados:    int = 0

    # ─── Método principal ─────────────────────────────────────
    def inspeccionar(self, neumatico: Neumatico) -> tuple[bool, list[dict]]:
        """
        Aplica todas las estrategias de calidad al neumático.

        Returns:
            (True,  [lista de resultados])  → neumático ACEPTADO (todas ok).
            (False, [lista de resultados])  → neumático RECHAZADO (algún fallo).
        """
        self.total_inspeccionados += 1
        resultados = []
        aprobado_global = True

        for regla in self._reglas:
            es_valido, mensaje = regla.evaluar(neumatico)   # ← Llamada Strategy
            resultados.append({
                "regla":    type(regla).__name__,
                "aprobado": es_valido,
                "detalle":  mensaje,
            })
            if not es_valido:
                aprobado_global = False

        if aprobado_global:
            self.total_aceptados += 1
            logger.info("ACEPTADO  — %s", neumatico.id_neumatico)
        else:
            self.total_rechazados += 1
            fallos = [r["detalle"] for r in resultados if not r["aprobado"]]
            logger.warning("RECHAZADO — %s | Fallos: %s",
                           neumatico.id_neumatico, fallos)

        return aprobado_global, resultados

    def estadisticas(self) -> dict:
        """Devuelve los contadores acumulados de la sesión."""
        return {
            "inspeccionados": self.total_inspeccionados,
            "aceptados":      self.total_aceptados,
            "rechazados":     self.total_rechazados,
        }
