"""
conftest.py — Subsistema B / tests
====================================
Garantiza que sys.path apunte a subsistema_b_calidad ANTES que a cualquier
otro módulo `modelos`, evitando colisiones de cache con Subsistema A.
"""
import sys
import os

# Directorio raíz del Subsistema B
SUBSISTEMA_B = os.path.join(os.path.dirname(__file__), "..")
SUBSISTEMA_B = os.path.normpath(SUBSISTEMA_B)

if SUBSISTEMA_B not in sys.path:
    sys.path.insert(0, SUBSISTEMA_B)

# Limpiar cache de 'modelos' para que se recargue desde B
# 1. Buscamos primero las claves que queremos borrar y las guardamos en una lista
claves_a_borrar = [key for key in sys.modules if key.startswith("modelos")]

# 2. Borramos esas claves del diccionario original
for key in claves_a_borrar:
    del sys.modules[key]