"""
main_b.py — Subsistema B (Servidor de Control de Calidad)
===========================================================
Punto de entrada del servidor Flask.

Uso:
    cd subsistema_b_calidad
    python main_b.py                    # puerto 5000 (default)
    python main_b.py --port 8080        # puerto personalizado
    python main_b.py --debug            # modo debug (no usar en producción)
"""
import argparse
import logging
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from api.rutas import api_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)


def crear_app() -> Flask:
    """
    Application Factory de Flask.
    Separa la creación de la app de su ejecución para facilitar los tests.
    """
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    return app


def main():
    parser = argparse.ArgumentParser(description="Subsistema B — Servidor de Calidad")
    parser.add_argument("--port",  type=int,  default=5000)
    parser.add_argument("--debug", action="store_true", default=False)
    args = parser.parse_args()

    app = crear_app()

    print(f"\n{'═'*55}")
    print("  SUBSISTEMA B — SERVIDOR DE CALIDAD ACTIVO")
    print(f"  URL: http://localhost:{args.port}/api/inspeccionar")
    print(f"  Stats: http://localhost:{args.port}/api/estadisticas")
    print(f"{'═'*55}\n")

    app.run(host="127.0.0.1", port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
