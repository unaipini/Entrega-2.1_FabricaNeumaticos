"""
Módulo: fabrica/fabrica_neumatico.py  —  Subsistema A (Planta)
================================================================
PATRÓN DE DISEÑO: FACTORY METHOD
----------------------------------
Problema : El código cliente no debe conocer los detalles de construcción
           de objetos Neumático ni los rangos válidos/defectuosos.
Solución : Clase abstracta FabricaNeumaticoBase con método de fábrica
           fabricar(). Tres implementaciones concretas:
             · FabricaNeumaticoValido    → siempre dentro de tolerancias.
             · FabricaNeumaticoDefecto   → siempre fuera de tolerancias.
             · FabricaNeumaticoAleatorio → mezcla 70/30 (válido/defecto).
"""
import random
import uuid
from abc import ABC, abstractmethod

from modelos.neumatico import Neumatico

# ── Rangos de negocio centralizados ──────────────────────────
RADIO_IDEAL = 16.0
RADIO_MIN   = 15.8
RADIO_MAX   = 16.2
PESO_MIN    = 9.0
PESO_MAX    = 10.0
HUELLA_MIN  = 1.6


# ═══════════════════════════════════════════════════════════════
#  FACTORY METHOD — Creador Abstracto
# ═══════════════════════════════════════════════════════════════
class FabricaNeumaticoBase(ABC):
    """
    [FACTORY METHOD — Creador Abstracto]
    Declara el método de fábrica que las subclases deben implementar.
    """

    @abstractmethod
    def fabricar(self) -> Neumatico:
        """Factory Method: las subclases definen QUÉ tipo de neumático crean."""
        raise NotImplementedError

    def _nuevo_id(self) -> str:
        return str(uuid.uuid4())


# ═══════════════════════════════════════════════════════════════
#  FACTORY METHOD — Creador Concreto 1: Válido
# ═══════════════════════════════════════════════════════════════
class FabricaNeumaticoValido(FabricaNeumaticoBase):
    """[FACTORY METHOD — Creador Concreto] Genera neumáticos dentro de tolerancias."""

    def fabricar(self) -> Neumatico:
        return Neumatico(
            id_neumatico=self._nuevo_id(),
            radio_pulgadas=round(random.uniform(RADIO_MIN, RADIO_MAX), 2),
            peso_kg=round(random.uniform(PESO_MIN, PESO_MAX), 3),
            profundidad_huella_mm=round(random.uniform(HUELLA_MIN, HUELLA_MIN + 5.0), 2),
        )


# ═══════════════════════════════════════════════════════════════
#  FACTORY METHOD — Creador Concreto 2: Defectuoso
# ═══════════════════════════════════════════════════════════════
class FabricaNeumaticoDefecto(FabricaNeumaticoBase):
    """[FACTORY METHOD — Creador Concreto] Genera neumáticos con al menos un defecto."""

    def fabricar(self) -> Neumatico:
        defecto = random.choice(["radio", "peso", "huella"])
        radio  = round(random.uniform(RADIO_MIN, RADIO_MAX), 2)
        peso   = round(random.uniform(PESO_MIN, PESO_MAX), 3)
        huella = round(random.uniform(HUELLA_MIN, HUELLA_MIN + 5.0), 2)

        if defecto == "radio":
            radio = round(random.choice([
                random.uniform(14.0, RADIO_MIN - 0.01),
                random.uniform(RADIO_MAX + 0.01, 18.0),
            ]), 2)
        elif defecto == "peso":
            peso = round(random.choice([
                random.uniform(5.0, PESO_MIN - 0.01),
                random.uniform(PESO_MAX + 0.01, 15.0),
            ]), 3)
        else:
            huella = round(random.uniform(0.0, HUELLA_MIN - 0.01), 2)

        return Neumatico(
            id_neumatico=self._nuevo_id(),
            radio_pulgadas=radio,
            peso_kg=peso,
            profundidad_huella_mm=huella,
        )


# ═══════════════════════════════════════════════════════════════
#  FACTORY METHOD — Creador Concreto 3: Aleatorio (línea real)
# ═══════════════════════════════════════════════════════════════
class FabricaNeumaticoAleatorio(FabricaNeumaticoBase):
    """
    [FACTORY METHOD — Creador Concreto]
    Simula la línea de producción: 70% válidos, 30% defectuosos.
    Delega en los otros Creadores Concretos (sin duplicar lógica).
    """
    PROBABILIDAD_VALIDO = 0.70

    def __init__(self):
        self._fabrica_valida  = FabricaNeumaticoValido()
        self._fabrica_defecto = FabricaNeumaticoDefecto()

    def fabricar(self) -> Neumatico:
        if random.random() < self.PROBABILIDAD_VALIDO:
            return self._fabrica_valida.fabricar()
        return self._fabrica_defecto.fabricar()
