"""
Módulo: modelos/neumatico.py  —  Subsistema B (Calidad)
========================================================
Entidad de dominio unificada. Incluye tanto a_dict() (para serialización
hacia la red) como desde_dict() (para deserialización desde JSON recibido).
Esto permite que en los tests de integración E2E se pueda cargar una sola
clase Neumatico que sirva tanto al cliente (A) como al servidor (B).
"""
from dataclasses import dataclass, asdict


@dataclass
class Neumatico:
    """
    Entidad principal del sistema (versión unificada).
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

    @classmethod
    def desde_dict(cls, datos: dict) -> "Neumatico":
        """Constructor alternativo desde el diccionario JSON de la petición."""
        return cls(
            id_neumatico=datos["id_neumatico"],
            radio_pulgadas=float(datos["radio_pulgadas"]),
            peso_kg=float(datos["peso_kg"]),
            profundidad_huella_mm=float(datos["profundidad_huella_mm"]),
        )

    def __repr__(self) -> str:
        return (
            f"Neumatico(id={self.id_neumatico!r}, "
            f"radio={self.radio_pulgadas}, "
            f"peso={self.peso_kg}, "
            f"huella={self.profundidad_huella_mm})"
        )
