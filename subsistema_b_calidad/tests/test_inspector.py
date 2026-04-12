"""
Tests Unitarios — InspectorCalidad (Contexto del Strategy)
===========================================================
Prueba que el Inspector:
  · Acepta cuando todas las estrategias aprueban.
  · Rechaza cuando al menos una estrategia falla.
  · Acumula correctamente los contadores de sesión.
  · Acepta estrategias inyectadas (permite mocking en otros tests).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import MagicMock

from modelos.neumatico import Neumatico
from servicio.inspector import InspectorCalidad
from estrategias.regla_calidad import ReglaCalidad


# ─── Helpers de fakes/mocks ──────────────────────────────────────────────────

class ReglaAprueba(ReglaCalidad):
    """Fake Strategy que siempre aprueba (para aislar el comportamiento del inspector)."""
    def evaluar(self, n): return True, "OK: fake"

class ReglaFalla(ReglaCalidad):
    """Fake Strategy que siempre falla."""
    def evaluar(self, n): return False, "FALLO: fake"

def _neumatico_fixture():
    return Neumatico("insp-test-001", 16.0, 9.5, 3.0)


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS — Decisión de inspección
# ═════════════════════════════════════════════════════════════════════════════

class TestInspectorDecision:

    def test_acepta_cuando_todas_las_reglas_aprueban(self):
        inspector = InspectorCalidad(reglas=[ReglaAprueba(), ReglaAprueba()])
        aprobado, _ = inspector.inspeccionar(_neumatico_fixture())
        assert aprobado is True

    def test_rechaza_cuando_una_regla_falla(self):
        inspector = InspectorCalidad(reglas=[ReglaAprueba(), ReglaFalla()])
        aprobado, _ = inspector.inspeccionar(_neumatico_fixture())
        assert aprobado is False

    def test_rechaza_cuando_todas_las_reglas_fallan(self):
        inspector = InspectorCalidad(reglas=[ReglaFalla(), ReglaFalla()])
        aprobado, _ = inspector.inspeccionar(_neumatico_fixture())
        assert aprobado is False

    def test_devuelve_resultado_por_cada_regla(self):
        inspector = InspectorCalidad(reglas=[ReglaAprueba(), ReglaFalla()])
        _, resultados = inspector.inspeccionar(_neumatico_fixture())
        assert len(resultados) == 2

    def test_resultado_contiene_nombre_de_regla(self):
        inspector = InspectorCalidad(reglas=[ReglaAprueba()])
        _, resultados = inspector.inspeccionar(_neumatico_fixture())
        assert resultados[0]["regla"] == "ReglaAprueba"

    def test_resultado_contiene_campo_aprobado(self):
        inspector = InspectorCalidad(reglas=[ReglaFalla()])
        _, resultados = inspector.inspeccionar(_neumatico_fixture())
        assert resultados[0]["aprobado"] is False

    def test_resultado_contiene_campo_detalle(self):
        inspector = InspectorCalidad(reglas=[ReglaAprueba()])
        _, resultados = inspector.inspeccionar(_neumatico_fixture())
        assert "detalle" in resultados[0]


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS — Contadores de sesión
# ═════════════════════════════════════════════════════════════════════════════

class TestInspectorContadores:

    def test_contadores_iniciales_son_cero(self):
        inspector = InspectorCalidad(reglas=[ReglaAprueba()])
        stats = inspector.estadisticas()
        assert stats["inspeccionados"] == 0
        assert stats["aceptados"]      == 0
        assert stats["rechazados"]     == 0

    def test_incrementa_inspeccionados(self):
        inspector = InspectorCalidad(reglas=[ReglaAprueba()])
        inspector.inspeccionar(_neumatico_fixture())
        inspector.inspeccionar(_neumatico_fixture())
        assert inspector.estadisticas()["inspeccionados"] == 2

    def test_incrementa_aceptados(self):
        inspector = InspectorCalidad(reglas=[ReglaAprueba()])
        inspector.inspeccionar(_neumatico_fixture())
        inspector.inspeccionar(_neumatico_fixture())
        assert inspector.estadisticas()["aceptados"] == 2
        assert inspector.estadisticas()["rechazados"] == 0

    def test_incrementa_rechazados(self):
        inspector = InspectorCalidad(reglas=[ReglaFalla()])
        inspector.inspeccionar(_neumatico_fixture())
        assert inspector.estadisticas()["rechazados"]  == 1
        assert inspector.estadisticas()["aceptados"]   == 0

    def test_contadores_mixtos(self):
        inspector = InspectorCalidad(reglas=[ReglaAprueba()])
        inspector2 = InspectorCalidad(reglas=[ReglaFalla()])
        # 3 aceptados y 2 rechazados
        for _ in range(3): inspector.inspeccionar(_neumatico_fixture())
        for _ in range(2): inspector2.inspeccionar(_neumatico_fixture())
        assert inspector.estadisticas() == {"inspeccionados": 3, "aceptados": 3, "rechazados": 0}
        assert inspector2.estadisticas() == {"inspeccionados": 2, "aceptados": 0, "rechazados": 2}
