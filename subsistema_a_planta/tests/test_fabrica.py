"""
Tests Unitarios — Subsistema A (Planta)
=========================================
Cobertura:
  · FabricaNeumaticoValido   → siempre produce neumáticos dentro de rangos.
  · FabricaNeumaticoDefecto  → siempre produce neumáticos con al menos un defecto.
  · FabricaNeumaticoAleatorio → tipo correcto, genera IDs únicos, delega bien.
  · Neumatico.a_dict()       → serialización correcta.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from modelos.neumatico import Neumatico
from fabrica.fabrica_neumatico import (
    FabricaNeumaticoValido,
    FabricaNeumaticoDefecto,
    FabricaNeumaticoAleatorio,
    RADIO_MIN, RADIO_MAX,
    PESO_MIN,  PESO_MAX,
    HUELLA_MIN,
)

# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def fabrica_valida():
    return FabricaNeumaticoValido()

@pytest.fixture
def fabrica_defecto():
    return FabricaNeumaticoDefecto()

@pytest.fixture
def fabrica_aleatoria():
    return FabricaNeumaticoAleatorio()


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _es_neumatico_valido(n: Neumatico) -> bool:
    return (
        RADIO_MIN <= n.radio_pulgadas <= RADIO_MAX
        and PESO_MIN <= n.peso_kg <= PESO_MAX
        and n.profundidad_huella_mm >= HUELLA_MIN
    )

def _tiene_algun_defecto(n: Neumatico) -> bool:
    return not _es_neumatico_valido(n)


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS UNITARIAS — FabricaNeumaticoValido
# ═════════════════════════════════════════════════════════════════════════════

class TestFabricaNeumaticoValido:

    def test_retorna_objeto_neumatico(self, fabrica_valida):
        """El Factory Method debe devolver una instancia de Neumatico."""
        resultado = fabrica_valida.fabricar()
        assert isinstance(resultado, Neumatico)

    def test_radio_dentro_del_rango(self, fabrica_valida):
        """Radio debe estar en [RADIO_MIN, RADIO_MAX]."""
        for _ in range(50):
            n = fabrica_valida.fabricar()
            assert RADIO_MIN <= n.radio_pulgadas <= RADIO_MAX, \
                f"Radio fuera de rango: {n.radio_pulgadas}"

    def test_peso_dentro_del_rango(self, fabrica_valida):
        """Peso debe estar en [PESO_MIN, PESO_MAX]."""
        for _ in range(50):
            n = fabrica_valida.fabricar()
            assert PESO_MIN <= n.peso_kg <= PESO_MAX, \
                f"Peso fuera de rango: {n.peso_kg}"

    def test_huella_por_encima_del_minimo(self, fabrica_valida):
        """Profundidad de huella debe ser >= HUELLA_MIN."""
        for _ in range(50):
            n = fabrica_valida.fabricar()
            assert n.profundidad_huella_mm >= HUELLA_MIN, \
                f"Huella insuficiente: {n.profundidad_huella_mm}"

    def test_id_no_es_nulo_ni_vacio(self, fabrica_valida):
        """El ID del neumático no debe ser nulo ni cadena vacía."""
        n = fabrica_valida.fabricar()
        assert n.id_neumatico
        assert isinstance(n.id_neumatico, str)

    def test_ids_son_unicos(self, fabrica_valida):
        """Cada llamada al Factory Method debe generar un ID único."""
        ids = {fabrica_valida.fabricar().id_neumatico for _ in range(100)}
        assert len(ids) == 100, "Se generaron IDs duplicados"


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS UNITARIAS — FabricaNeumaticoDefecto
# ═════════════════════════════════════════════════════════════════════════════

class TestFabricaNeumaticoDefecto:

    def test_retorna_objeto_neumatico(self, fabrica_defecto):
        resultado = fabrica_defecto.fabricar()
        assert isinstance(resultado, Neumatico)

    def test_siempre_genera_al_menos_un_defecto(self, fabrica_defecto):
        """Todos los neumáticos defectuosos deben fallar al menos una regla."""
        for _ in range(100):
            n = fabrica_defecto.fabricar()
            assert _tiene_algun_defecto(n), \
                f"Se generó un neumático válido en FabricaDefecto: {n}"


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS UNITARIAS — FabricaNeumaticoAleatorio
# ═════════════════════════════════════════════════════════════════════════════

class TestFabricaNeumaticoAleatorio:

    def test_retorna_objeto_neumatico(self, fabrica_aleatoria):
        resultado = fabrica_aleatoria.fabricar()
        assert isinstance(resultado, Neumatico)

    def test_genera_ids_unicos(self, fabrica_aleatoria):
        ids = {fabrica_aleatoria.fabricar().id_neumatico for _ in range(200)}
        assert len(ids) == 200

    def test_produce_ambos_tipos_en_muestra_grande(self, fabrica_aleatoria):
        """Con 200 neumáticos debe haber al menos alguno válido y alguno defectuoso."""
        validos   = sum(1 for _ in range(200) if _es_neumatico_valido(fabrica_aleatoria.fabricar()))
        defectuosos = 200 - validos
        assert validos   > 0, "Nunca se generó un neumático válido"
        assert defectuosos > 0, "Nunca se generó un neumático defectuoso"


# ═════════════════════════════════════════════════════════════════════════════
#  PRUEBAS UNITARIAS — Serialización Neumatico.a_dict()
# ═════════════════════════════════════════════════════════════════════════════

class TestNeumaticoDominio:

    def test_a_dict_contiene_todos_los_campos(self):
        n = Neumatico(
            id_neumatico="test-id-001",
            radio_pulgadas=16.0,
            peso_kg=9.5,
            profundidad_huella_mm=3.2,
        )
        d = n.a_dict()
        assert set(d.keys()) == {"id_neumatico", "radio_pulgadas", "peso_kg", "profundidad_huella_mm"}

    def test_a_dict_valores_correctos(self):
        n = Neumatico("abc", 15.9, 9.8, 2.1)
        d = n.a_dict()
        assert d["id_neumatico"]          == "abc"
        assert d["radio_pulgadas"]        == 15.9
        assert d["peso_kg"]               == 9.8
        assert d["profundidad_huella_mm"] == 2.1
