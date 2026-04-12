"""
conftest.py — Subsistema A / tests
====================================
Garantiza que sys.path apunte a subsistema_a_planta al ejecutar tests de A.
"""
import sys
import os

SUBSISTEMA_A = os.path.join(os.path.dirname(__file__), "..")
SUBSISTEMA_A = os.path.normpath(SUBSISTEMA_A)

if SUBSISTEMA_A not in sys.path:
    sys.path.insert(0, SUBSISTEMA_A)
