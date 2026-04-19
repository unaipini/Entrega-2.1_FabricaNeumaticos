"""
Tests Unitarios — Subsistema B (Calidad)
==========================================
Cobertura de LÍMITES para cada Estrategia (Strategy Pattern).
Los tests de límites son esenciales: verifican el comportamiento
exacto en los valores frontera de las reglas de negocio.

Reglas de equivalencia probadas:
  ┌──────────────────┬──────────────┬──────────────┬──────────────┐
  │ Atributo         │ Justo abajo  │ Límite       │ Justo encima │
  ├──────────────────┼──────────────┼──────────────┼──────────────┤
  │ radio_pulgadas   │ 15.79 (FAIL) │ 15.8 (OK)    │ 16.2 (OK)    │
  │                  │              │ 16.2 (OK)    │ 16.21 (FAIL) │
  │ peso_kg          │ 8.99  (FAIL) │ 9.0  (OK)    │ 10.0 (OK)    │
  │                  │              │ 10.0 (OK)    │ 10.01 (FAIL) │
  │ huella_mm        │ 1.59  (FAIL) │ 1.6  (OK)    │ 5.0  (OK)    │
  └──────────────────┴──────────────┴──────────────┴──────────────┘
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from modelos.neumatico import Neumatico
from estrategias.reglas_concretas import ReglaRadio, ReglaPeso, ReglaHuella


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _neumatico(**kwargs) -> Neumatico:
    """Crea un Neumatico válido de base y sobreescribe los campos indicados."""
    base = {
        "id_neumatico": "test-unit",
        "radio_pulgadas": 16.0,
        "peso_kg": 9.5,
        "profundidad_huella_mm": 3.0,
    }
    base.update(kwargs)
    return Neumatico(**base)


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS UNITARIAS — ReglaRadio (límites de valor)
# ═════════════════════════════════════════════════════════════════════════════

class TestReglaRadio:
    regla = ReglaRadio()

    # Casos VÁLIDOS ────────────────────────────────
    def test_radio_limite_inferior_exacto_aprueba(self):
        ok, _ = self.regla.evaluar(_neumatico(radio_pulgadas=15.8))
        assert ok is True

    def test_radio_limite_superior_exacto_aprueba(self):
        ok, _ = self.regla.evaluar(_neumatico(radio_pulgadas=16.2))
        assert ok is True

    def test_radio_ideal_aprueba(self):
        ok, _ = self.regla.evaluar(_neumatico(radio_pulgadas=16.0))
        assert ok is True

    def test_radio_interior_aprueba(self):
        ok, _ = self.regla.evaluar(_neumatico(radio_pulgadas=16.1))
        assert ok is True

    # Casos INVÁLIDOS ──────────────────────────────
    def test_radio_justo_debajo_limite_inferior_falla(self):
        ok, msg = self.regla.evaluar(_neumatico(radio_pulgadas=15.79))
        assert ok is False
        assert "FALLO" in msg

    def test_radio_justo_encima_limite_superior_falla(self):
        ok, msg = self.regla.evaluar(_neumatico(radio_pulgadas=16.21))
        assert ok is False
        assert "FALLO" in msg

    def test_radio_muy_pequenio_falla(self):
        ok, _ = self.regla.evaluar(_neumatico(radio_pulgadas=10.0))
        assert ok is False

    def test_radio_muy_grande_falla(self):
        ok, _ = self.regla.evaluar(_neumatico(radio_pulgadas=20.0))
        assert ok is False

    def test_mensaje_contiene_valor_del_radio(self):
        _, msg = self.regla.evaluar(_neumatico(radio_pulgadas=14.5))
        assert "14.5" in msg


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS UNITARIAS — ReglaPeso (límites de valor)
# ═════════════════════════════════════════════════════════════════════════════

class TestReglaPeso:
    regla = ReglaPeso()

    # Casos VÁLIDOS ────────────────────────────────
    def test_peso_limite_inferior_exacto_aprueba(self):
        ok, _ = self.regla.evaluar(_neumatico(peso_kg=9.0))
        assert ok is True

    def test_peso_limite_superior_exacto_aprueba(self):
        ok, _ = self.regla.evaluar(_neumatico(peso_kg=10.0))
        assert ok is True

    def test_peso_interior_aprueba(self):
        ok, _ = self.regla.evaluar(_neumatico(peso_kg=9.5))
        assert ok is True

    # Casos INVÁLIDOS ──────────────────────────────
    def test_peso_justo_debajo_limite_inferior_falla(self):
        ok, msg = self.regla.evaluar(_neumatico(peso_kg=8.99))
        assert ok is False
        assert "FALLO" in msg

    def test_peso_justo_encima_limite_superior_falla(self):
        ok, msg = self.regla.evaluar(_neumatico(peso_kg=10.01))
        assert ok is False
        assert "FALLO" in msg

    def test_peso_cero_falla(self):
        ok, _ = self.regla.evaluar(_neumatico(peso_kg=0.0))
        assert ok is False

    def test_mensaje_contiene_valor_del_peso(self):
        _, msg = self.regla.evaluar(_neumatico(peso_kg=5.5))
        assert "5.5" in msg


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS UNITARIAS — ReglaHuella (límites de valor)
# ═════════════════════════════════════════════════════════════════════════════

class TestReglaHuella:
    regla = ReglaHuella()

    # Casos VÁLIDOS ────────────────────────────────
    def test_huella_en_exactamente_minimo_aprueba(self):
        ok, _ = self.regla.evaluar(_neumatico(profundidad_huella_mm=1.6))
        assert ok is True

    def test_huella_mayor_que_minimo_aprueba(self):
        ok, _ = self.regla.evaluar(_neumatico(profundidad_huella_mm=5.0))
        assert ok is True

    def test_huella_muy_grande_aprueba(self):
        ok, _ = self.regla.evaluar(_neumatico(profundidad_huella_mm=12.0))
        assert ok is True

    # Casos INVÁLIDOS ──────────────────────────────
    def test_huella_justo_debajo_minimo_falla(self):
        ok, msg = self.regla.evaluar(_neumatico(profundidad_huella_mm=1.59))
        assert ok is False
        assert "FALLO" in msg

    def test_huella_cero_falla(self):
        ok, _ = self.regla.evaluar(_neumatico(profundidad_huella_mm=0.0))
        assert ok is False

    def test_huella_negativa_falla(self):
        ok, _ = self.regla.evaluar(_neumatico(profundidad_huella_mm=-1.0))
        assert ok is False

    def test_mensaje_contiene_valor_de_huella(self):
        _, msg = self.regla.evaluar(_neumatico(profundidad_huella_mm=0.5))
        assert "0.5" in msg
