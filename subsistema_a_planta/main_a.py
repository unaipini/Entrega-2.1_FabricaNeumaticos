"""
main_a.py — Subsistema A (Planta de Fabricación)
=================================================
Uso:
    cd subsistema_a_planta
    python main_a.py          # 5 neumáticos (default)
    python main_a.py --n 10   # 10 neumáticos
"""
import argparse
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fabrica.fabrica_neumatico import FabricaNeumaticoAleatorio
from cliente.cliente_api import ClienteCalidad

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("SubsistemaA")


def main():
    parser = argparse.ArgumentParser(description="Subsistema A — Planta de Neumáticos")
    parser.add_argument("--n", type=int, default=5, help="Neumáticos a fabricar")
    args = parser.parse_args()

    fabrica = FabricaNeumaticoAleatorio()   # ← Factory Method
    cliente = ClienteCalidad()
    contadores = {"red_aceptado": 0, "red_rechazado": 0, "local": 0}

    logger.info("═" * 60)
    logger.info("  SUBSISTEMA A — INICIO DE PRODUCCIÓN (%d neumáticos)", args.n)
    logger.info("═" * 60)

    for i in range(1, args.n + 1):
        neumatico = fabrica.fabricar()
        logger.info("[%d/%d] Fabricado → %s", i, args.n, neumatico)
        resultado = cliente.enviar(neumatico)
        modo  = resultado["modo"]
        estado = resultado["resultado"]
        logger.info("       Enviado [%s] → HTTP %s → %s",
                    modo.upper(), resultado.get("status", "—"), estado)
        if modo == "local":
            contadores["local"] += 1
        elif estado == "ACEPTADO":
            contadores["red_aceptado"] += 1
        else:
            contadores["red_rechazado"] += 1

    logger.info("═" * 60)
    logger.info("  RESUMEN: Aceptados=%d | Rechazados=%d | Local=%d",
                contadores["red_aceptado"], contadores["red_rechazado"], contadores["local"])
    logger.info("═" * 60)


if __name__ == "__main__":
    main()
