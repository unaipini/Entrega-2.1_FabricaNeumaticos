"""
Módulo: estrategias/reglas_concretas.py  —  Subsistema B (Calidad)
====================================================================
PATRÓN DE DISEÑO: STRATEGY — Implementaciones Concretas
---------------------------------------------------------
Cada clase implementa la interfaz ReglaCalidad y encapsula
UN único criterio de calidad, siguiendo el Principio de
Responsabilidad Única (SRP).

El Inspector (contexto del patrón Strategy) recibirá una lista
de estas estrategias y las ejecutará en secuencia.
"""
from estrategias.regla_calidad import ReglaCalidad
from modelos.neumatico import Neumatico

# ── Constantes de negocio (fuente única de verdad) ────────────
RADIO_MIN   = 15.8
RADIO_MAX   = 16.2
PESO_MIN    = 9.0
PESO_MAX    = 10.0
HUELLA_MIN  = 1.6   # mm — cualquier valor >= 1.6 es válido


# ═══════════════════════════════════════════════════════════════
#  STRATEGY — Implementación Concreta 1: ReglaRadio
# ═══════════════════════════════════════════════════════════════
class ReglaRadio(ReglaCalidad):
    """
    [STRATEGY — Concreto]
    Verifica que el radio del neumático esté en [15.8, 16.2] pulgadas.
    """

    def evaluar(self, neumatico: Neumatico) -> tuple[bool, str]:
        r = neumatico.radio_pulgadas
        if RADIO_MIN <= r <= RADIO_MAX:
            return True, f"OK: radio={r} pulgadas dentro de [{RADIO_MIN}, {RADIO_MAX}]"
        return False, (
            f"FALLO: radio={r} pulgadas fuera del rango permitido "
            f"[{RADIO_MIN}, {RADIO_MAX}]"
        )


# ═══════════════════════════════════════════════════════════════
#  STRATEGY — Implementación Concreta 2: ReglaPeso
# ═══════════════════════════════════════════════════════════════
class ReglaPeso(ReglaCalidad):
    """
    [STRATEGY — Concreto]
    Verifica que el peso del neumático esté en [9.0, 10.0] kg.
    """

    def evaluar(self, neumatico: Neumatico) -> tuple[bool, str]:
        p = neumatico.peso_kg
        if PESO_MIN <= p <= PESO_MAX:
            return True, f"OK: peso={p} kg dentro de [{PESO_MIN}, {PESO_MAX}]"
        return False, (
            f"FALLO: peso={p} kg fuera del rango permitido "
            f"[{PESO_MIN}, {PESO_MAX}]"
        )


# ═══════════════════════════════════════════════════════════════
#  STRATEGY — Implementación Concreta 3: ReglaHuella
# ═══════════════════════════════════════════════════════════════
class ReglaHuella(ReglaCalidad):
    """
    [STRATEGY — Concreto]
    Verifica que la profundidad de huella sea >= 1.6 mm.
    (Norma de seguridad vial mínima internacional.)
    """

    def evaluar(self, neumatico: Neumatico) -> tuple[bool, str]:
        h = neumatico.profundidad_huella_mm
        if h >= HUELLA_MIN:
            return True, f"OK: huella={h} mm >= mínimo {HUELLA_MIN} mm"
        return False, (
            f"FALLO: huella={h} mm por debajo del mínimo "
            f"de seguridad de {HUELLA_MIN} mm"
        )
