"""
Módulo: estrategias/regla_calidad.py  —  Subsistema B (Calidad)
================================================================
PATRÓN DE DISEÑO: STRATEGY
---------------------------
Problema : El algoritmo de evaluación de calidad puede cambiar (nuevas
           normas ISO, tolerancias distintas) sin que la clase Inspector
           deba modificarse.
Solución : Se define la interfaz ReglaCalidad (Strategy abstracta).
           Cada criterio de calidad es una clase concreta que implementa
           esta interfaz.  El Inspector recibe una lista de estrategias
           y las ejecuta sin conocer sus implementaciones internas.

Estructura:
    ReglaCalidad          ← Interfaz (Strategy abstracta)
    ├── ReglaRadio        ← Estrategia concreta (radio en pulgadas)
    ├── ReglaPeso         ← Estrategia concreta (peso en kg)
    └── ReglaHuella       ← Estrategia concreta (profundidad de huella mm)
"""
from abc import ABC, abstractmethod
from modelos.neumatico import Neumatico


# ═══════════════════════════════════════════════════════════════
#  STRATEGY — Interfaz abstracta
# ═══════════════════════════════════════════════════════════════
class ReglaCalidad(ABC):
    """
    [STRATEGY — Interfaz]
    Contrato que deben cumplir todas las reglas de evaluación de calidad.
    El método evaluar() devuelve (bool, str): (es_valido, motivo).
    """

    @abstractmethod
    def evaluar(self, neumatico: Neumatico) -> tuple[bool, str]:
        """
        Evalúa si el neumático cumple esta regla.

        Returns:
            (True,  "OK: ...")       → cumple la regla.
            (False, "FALLO: ...")    → viola la regla (motivo del rechazo).
        """
        raise NotImplementedError
