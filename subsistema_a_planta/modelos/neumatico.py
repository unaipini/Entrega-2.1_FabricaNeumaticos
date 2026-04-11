"""
Módulo: modelos/neumatico.py  —  Subsistema A (Planta)
Responsabilidad: Define la entidad de dominio Neumático.
"""
from dataclasses import dataclass, asdict


@dataclass
class Neumatico:
    """
    Entidad principal del sistema.
    Atributos:
        id_neumatico          (str)  : Identificador único (UUID).
        radio_pulgadas        (float): Rango válido [15.8, 16.2].
        peso_kg               (float): Rango válido [9.0, 10.0].
        profundidad_huella_mm (float): Válido si >= 1.6.
    """
    id_neumatico: str
    radio_pulgadas: float
    peso_kg: float
    profundidad_huella_mm: float

    def a_dict(self) -> dict:
        """Serializa el neumático a diccionario para JSON/API REST."""
        return asdict(self)

    def __repr__(self) -> str:
        return (
            f"Neumatico(id={self.id_neumatico!r}, "
            f"radio={self.radio_pulgadas}, "
            f"peso={self.peso_kg}, "
            f"huella={self.profundidad_huella_mm})"
        )
