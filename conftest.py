"""
conftest.py — raíz del proyecto
================================
Gestión de sys.path para que pytest pueda ejecutar TODAS las suites
desde el directorio raíz sin conflictos de cache de módulos.

Cada subsistema tiene su propio espacio de nombres gracias al orden
de inserción en sys.path gestionado aquí.
"""
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PATH_A = os.path.join(ROOT, "subsistema_a_planta")
PATH_B = os.path.join(ROOT, "subsistema_b_calidad")

# Insertar ambos al inicio; B tiene prioridad (insertado último = índice 0)
for p in [PATH_A, PATH_B]:
    if p not in sys.path:
        sys.path.insert(0, p)
